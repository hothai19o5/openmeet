"""
Local Whisper STT Adapter — Option A
Sử dụng faster-whisper (CTranslate2 backend) — nhẹ, chạy CPU, không cần API key.

Đặc điểm:
- Không có speaker diarization (speaker=None)
- Segment-level timestamps (không word-level)
- VAD filter built-in
- RAM: ~500MB (base model), phù hợp VPS 2GB

Cài đặt: pip install faster-whisper
"""

import os
import logging
import tempfile
import asyncio
from typing import AsyncIterator

from ports.stt_port import STTPort, TranscriptionResult, TranscriptionSegment

logger = logging.getLogger(__name__)


class LocalWhisperAdapter(STTPort):
    """
    Adapter thực thi STTPort bằng faster-whisper chạy local.
    Không cần API key, không cần Internet. Phù hợp máy yếu (dùng model tiny/base).

    supports_diarization = False — không phân biệt speaker.
    """

    def __init__(self, model_size: str = "base", device: str = "cpu"):
        self.model_size = model_size
        self.device = device
        self._model = None
        self._lock = asyncio.Lock()

    def _ensure_model(self):
        """Lazy load model lần đầu gọi (tránh load memory khi chưa cần)."""
        if self._model is None:
            from faster_whisper import WhisperModel
            logger.info(f"Loading faster-whisper model '{self.model_size}' on {self.device}...")
            self._model = WhisperModel(self.model_size, device=self.device, compute_type="int8")
            logger.info("faster-whisper model loaded successfully.")
        return self._model

    async def transcribe(
        self, audio_data: bytes, *, language: str = "vi", sample_rate: int = 16000
    ) -> TranscriptionResult:
        """Chuyển đổi audio bytes → text bằng local faster-whisper."""
        loop = asyncio.get_event_loop()

        def _do_transcribe():
            model = self._ensure_model()
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:
                f.write(audio_data)
                f.flush()
                segments, info = model.transcribe(
                    f.name,
                    language=language,
                    beam_size=1,
                    vad_filter=True,
                )
                # Convert generator → list (tránh file bị xoá trước khi iterate)
                seg_list = list(segments)

                full_text = " ".join(seg.text.strip() for seg in seg_list)

                # Build TranscriptionSegment list (không có speaker)
                ts_segments = [
                    TranscriptionSegment(
                        text=seg.text.strip(),
                        speaker=None,          # faster-whisper không có diarization
                        start_time=seg.start,
                        end_time=seg.end,
                        confidence=None,
                    )
                    for seg in seg_list
                ]

                return TranscriptionResult(
                    text=full_text.strip(),
                    language=info.language,
                    confidence=None,
                    is_final=True,
                    segments=ts_segments,
                )

        async with self._lock:
            return await loop.run_in_executor(None, _do_transcribe)

    async def transcribe_stream(
        self, audio_stream: AsyncIterator[bytes], *, language: str = "vi"
    ) -> AsyncIterator[TranscriptionResult]:
        """
        Streaming: gom audio chunks thành buffer, transcribe theo cửa sổ (~3 giây).
        """
        buffer = bytearray()
        segment_id = 0
        # ~3 giây audio ở 16kHz, 16-bit = ~96000 bytes
        chunk_threshold = 96000

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
        """Giải phóng model khỏi memory."""
        if self._model is not None:
            del self._model
            self._model = None
            logger.info("faster-whisper model unloaded.")

    @property
    def supports_diarization(self) -> bool:
        return False
