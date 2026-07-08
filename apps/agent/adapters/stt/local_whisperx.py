"""
Local WhisperX STT Adapter — Option C
WhisperX + pyannote.audio 3.1 — full speaker diarization + word-level alignment.

Pipeline:
  1. WhisperX load model (Whisper) → transcribe → segments với word-level timestamps
  2. pyannote.audio 3.1 → diarize audio → speaker segments (SPEAKER_00, SPEAKER_01, ...)
  3. Assign each whisper word → matching speaker → merge thành final segments

Yêu cầu:
  - pip install whisperx torch torchaudio pyannote.audio
  - HuggingFace token (pyannote models cần accept license + download)
  - GPU recommended (CPU chạy được nhưng chậm, ~5-10x realtime)
  - RAM: ~3-4GB (Whisper large-v3 + pyannote + wav2vec2)

Sub-points:
  - pyannote 3.1 chỉ hỗ trợ 16kHz mono audio → cần resample
  - HF_TOKEN: accept license tại huggingface.co/pyannote/speaker-diarization-3.1
"""

import os
import logging
import tempfile
import asyncio
from typing import AsyncIterator

from ports.stt_port import STTPort, TranscriptionResult, TranscriptionSegment

logger = logging.getLogger(__name__)


class LocalWhisperXAdapter(STTPort):
    """
    Adapter thực thi STTPort bằng WhisperX + pyannote.audio 3.1.

    supports_diarization = True — phân biệt speaker tự động.
    Word-level alignment — timestamp chính xác tới từng từ.

    Cấu hình:
      whisper_model: large-v3 | medium | base | small | tiny
      device: cuda | cpu
      compute_type: float16 (GPU) | int8 (CPU)
      hf_token: HuggingFace token (cần accept pyannote license)
      min_speakers / max_speakers: optional, để None thì auto-detect
    """

    def __init__(
        self,
        model_size: str = "large-v3",
        device: str = "cuda",
        compute_type: str | None = None,
        hf_token: str | None = None,
        min_speakers: int | None = None,
        max_speakers: int | None = None,
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type or ("float16" if device == "cuda" else "int8")
        self.hf_token = hf_token or os.getenv("HF_TOKEN", "") or os.getenv("HUGGINGFACE_TOKEN", "")
        self.min_speakers = min_speakers
        self.max_speakers = max_speakers

        self._model = None
        self._diarize_pipeline = None
        self._align_model = None
        self._meta = None
        self._lock = asyncio.Lock()

    def _ensure_models(self):
        """Lazy load tất cả models lần đầu gọi."""
        if self._model is not None:
            return

        import whisperx
        logger.info(f"Loading WhisperX model '{self.model_size}' on {self.device} ({self.compute_type})...")

        # 1. Load Whisper model
        self._model = whisperx.load_model(
            self.model_size,
            device=self.device,
            compute_type=self.compute_type,
        )
        logger.info("WhisperX model loaded.")

        # 2. Load alignment model (wav2vec2) — cho word-level timestamps
        language = "vi"  # default, sẽ override khi transcribe
        try:
            self._align_model, self._meta = whisperx.load_align_model(
                language_code=language,
                device=self.device,
            )
            logger.info(f"Alignment model loaded for language '{language}'.")
        except Exception as e:
            logger.warning(f"Could not load alignment model for '{language}': {e}")
            self._align_model = None
            self._meta = None

        # 3. Load pyannote diarization pipeline
        if self.hf_token:
            from pyannote.audio import Pipeline
            logger.info("Loading pyannote diarization pipeline (3.1)...")
            self._diarize_pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=self.hf_token,
            )
            if self.device == "cuda":
                import torch
                self._diarize_pipeline.to(torch.device("cuda"))
            logger.info("pyannote diarization pipeline loaded.")
        else:
            logger.warning(
                "No HuggingFace token provided (HF_TOKEN). "
                "Diarization disabled — speaker info will be None."
            )
            self._diarize_pipeline = None

    def _reload_align_model(self, language: str):
        """Reload alignment model nếu language khác với model hiện tại."""
        if self._align_model is not None and self._meta and self._meta.get("language") == language:
            return  # đã đúng language

        import whisperx
        try:
            self._align_model, self._meta = whisperx.load_align_model(
                language_code=language,
                device=self.device,
            )
            logger.info(f"Alignment model reloaded for language '{language}'.")
        except Exception as e:
            logger.warning(f"Could not load alignment model for '{language}': {e}")
            self._align_model = None
            self._meta = None

    async def transcribe(
        self, audio_data: bytes, *, language: str = "vi", sample_rate: int = 16000
    ) -> TranscriptionResult:
        """
        Full pipeline: WhisperX transcribe → align → diarize → assign speakers.
        """
        loop = asyncio.get_event_loop()

        def _do_transcribe():
            import whisperx

            self._ensure_models()
            self._reload_align_model(language)

            # Write audio to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:
                f.write(audio_data)
                f.flush()

                # Load audio với whisperx (tự resample về 16kHz mono)
                audio = whisperx.load_audio(f.name)

                # Step 1: Transcribe
                logger.info("WhisperX: transcribing...")
                result = self._model.transcribe(audio, language=language, batch_size=8)

                # Step 2: Word-level alignment
                if self._align_model is not None:
                    logger.info("WhisperX: aligning words...")
                    result = whisperx.align(
                        result["segments"],
                        self._align_model,
                        self._meta,
                        audio,
                        self.device,
                        return_char_alignments=False,
                    )

                # Step 3: Diarization
                if self._diarize_pipeline is not None:
                    logger.info("WhisperX: running diarization (pyannote 3.1)...")
                    diarize_segments = self._diarize_pipeline(
                        audio,
                        min_speakers=self.min_speakers,
                        max_speakers=self.max_speakers,
                    )
                    # Assign speakers to word segments
                    result = whisperx.assign_word_speakers(diarize_segments, result)
                    logger.info("Diarization complete.")

                # Build TranscriptionSegment list
                ts_segments = []
                full_text_parts = []

                for seg in result.get("segments", []):
                    speaker = seg.get("speaker", None)
                    seg_text = seg.get("text", "").strip()
                    start = seg.get("start", 0.0)
                    end = seg.get("end", 0.0)

                    ts_segments.append(TranscriptionSegment(
                        text=seg_text,
                        speaker=speaker,
                        start_time=start,
                        end_time=end,
                        confidence=None,
                    ))
                    full_text_parts.append(seg_text)

                full_text = " ".join(full_text_parts).strip()

                total_start = ts_segments[0].start_time if ts_segments else 0.0
                total_end = ts_segments[-1].end_time if ts_segments else 0.0
                detected_language = result.get("language", language)

                return TranscriptionResult(
                    text=full_text,
                    language=detected_language,
                    confidence=None,
                    is_final=True,
                    segments=ts_segments,
                    start_time=total_start,
                    end_time=total_end,
                )

        async with self._lock:
            return await loop.run_in_executor(None, _do_transcribe)

    async def transcribe_stream(
        self, audio_stream: AsyncIterator[bytes], *, language: str = "vi"
    ) -> AsyncIterator[TranscriptionResult]:
        """
        Streaming: gom audio chunks ~10 giây rồi chạy full pipeline.
        WhisperX cần buffer lớn hơn faster-whisper vì diarization cần context.

        10 giây @ 16kHz 16-bit = 320000 bytes
        """
        buffer = bytearray()
        segment_id = 0
        chunk_threshold = 320000  # ~10 giây

        async for chunk in audio_stream:
            buffer.extend(chunk)
            if len(buffer) >= chunk_threshold:
                audio_bytes = bytes(buffer)
                buffer.clear()
                result = await self.transcribe(audio_bytes, language=language)
                result.segment_id = segment_id
                result.is_final = False
                segment_id += 1
                yield result

        # Flush buffer còn dư
        if buffer:
            result = await self.transcribe(bytes(buffer), language=language)
            result.segment_id = segment_id
            result.is_final = True
            yield result

    async def close(self) -> None:
        """Giải phóng tất cả models khỏi memory."""
        self._model = None
        self._diarize_pipeline = None
        self._align_model = None
        self._meta = None
        # PyTorch cache cleanup
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
        except ImportError:
            pass
        logger.info("WhisperX models unloaded.")

    @property
    def supports_diarization(self) -> bool:
        return True
