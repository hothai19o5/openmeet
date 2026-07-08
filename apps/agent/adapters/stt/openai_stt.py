"""
OpenAI-compatible STT Adapter — Option B
Gọi API transcription format OpenAI (hoặc Groq, vLLM, bất kỳ endpoint nào tương thích).

Endpoint: POST /v1/audio/transcriptions
Format: multipart/form-data với file audio

Tương thích: OpenAI Whisper API, Groq, Azure OpenAI, vLLM audio, ...

Đặc điểm:
- Không có speaker diarization (API không trả speaker info)
- Không có timestamps (trừ verbose_json format — support nhưng optional)
- RAM: ~0 (gọi remote API)
- Speed: phụ thuộc network + API latency
"""

import os
import logging
import asyncio
import tempfile
from typing import AsyncIterator

import httpx

from ports.stt_port import STTPort, TranscriptionResult, TranscriptionSegment

logger = logging.getLogger(__name__)


class OpenAISTTAdapter(STTPort):
    """
    Adapter thực thi STTPort bằng OpenAI-compatible API.
    Dùng được cho OpenAI, Groq, Azure, hoặc bất kỳ server nào tuân thủ format.

    supports_diarization = False — API không trả speaker info.
    supports_timestamps = True (khi response_format=verbose_json).
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.openai.com/v1",
        model: str = "whisper-1",
        response_format: str = "verbose_json",
    ):
        self.api_key = api_key or os.getenv("OPENAI_STT_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.response_format = response_format
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=60.0,
        )

    async def transcribe(
        self, audio_data: bytes, *, language: str = "vi", sample_rate: int = 16000
    ) -> TranscriptionResult:
        """Gọi API transcription. Dùng verbose_json để lấy timestamps nếu API hỗ trợ."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:
            f.write(audio_data)
            f.flush()

            with open(f.name, "rb") as audio_file:
                files = {"file": ("audio.wav", audio_file, "audio/wav")}
                data = {
                    "model": self.model,
                    "language": language,
                    "response_format": self.response_format,
                }
                response = await self._client.post(
                    "/audio/transcriptions",
                    files=files,
                    data=data,
                )
                response.raise_for_status()
                result = response.json()

                # verbose_json format: có "segments" với start/end timestamps
                api_segments = result.get("segments", [])

                if api_segments:
                    ts_segments = [
                        TranscriptionSegment(
                            text=seg.get("text", "").strip(),
                            speaker=None,      # API không trả speaker info
                            start_time=seg.get("start", 0.0),
                            end_time=seg.get("end", 0.0),
                            confidence=None,
                        )
                        for seg in api_segments
                    ]
                    full_text = " ".join(s.text for s in ts_segments)
                else:
                    # Fallback: plain json format (chỉ có "text")
                    ts_segments = []
                    full_text = result.get("text", "").strip()

                # Tính start/end tổng
                total_start = ts_segments[0].start_time if ts_segments else 0.0
                total_end = ts_segments[-1].end_time if ts_segments else 0.0

                return TranscriptionResult(
                    text=full_text.strip(),
                    language=result.get("language", language),
                    confidence=None,
                    is_final=True,
                    segments=ts_segments,
                    start_time=total_start,
                    end_time=total_end,
                )

    async def transcribe_stream(
        self, audio_stream: AsyncIterator[bytes], *, language: str = "vi"
    ) -> AsyncIterator[TranscriptionResult]:
        """
        Streaming: gom chunks lại theo cửa sổ 3 giây rồi gọi API.
        OpenAI Whisper API chưa support streaming thật, nên đây là semi-streaming.
        """
        buffer = bytearray()
        segment_id = 0
        chunk_threshold = 96000  # ~3 giây @ 16kHz 16-bit

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

        if buffer:
            result = await self.transcribe(bytes(buffer), language=language)
            result.segment_id = segment_id
            result.is_final = True
            yield result

    async def close(self) -> None:
        await self._client.aclose()
        logger.info("OpenAI STT client closed.")

    @property
    def supports_diarization(self) -> bool:
        return False
