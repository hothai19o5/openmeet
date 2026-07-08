"""
OpenAI-compatible STT Adapter
Gọi API transcription format OpenAI (hoặc Groq, vLLM, bất kỳ endpoint nào tương thích).

Endpoint: POST /v1/audio/transcriptions
Format: multipart/form-data với file audio

Tương thích: OpenAI Whisper API, Groq, Azure OpenAI, vLLM audio, ...
"""

import os
import logging
import asyncio
import tempfile
from typing import AsyncIterator

import httpx

from ports.stt_port import STTPort, TranscriptionResult

logger = logging.getLogger(__name__)


class OpenAISTTAdapter(STTPort):
    """
    Adapter thực thi STTPort bằng OpenAI-compatible API.
    Vaan: dùng được cho OpenAI, Groq, Azure, hoặc bất kỳ server nào tuân thủ format.
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.openai.com/v1",
        model: str = "whisper-1",
    ):
        self.api_key = api_key or os.getenv("OPENAI_STT_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=60.0,
        )

    async def transcribe(
        self, audio_data: bytes, *, language: str = "vi", sample_rate: int = 16000
    ) -> TranscriptionResult:
        """Gọi API transcription."""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:
            f.write(audio_data)
            f.flush()

            with open(f.name, "rb") as audio_file:
                files = {"file": ("audio.wav", audio_file, "audio/wav")}
                data = {
                    "model": self.model,
                    "language": language,
                    "response_format": "json",
                }
                response = await self._client.post(
                    "/audio/transcriptions",
                    files=files,
                    data=data,
                )
                response.raise_for_status()
                result = response.json()
                return TranscriptionResult(
                    text=result.get("text", "").strip(),
                    language=result.get("language", language),
                    confidence=None,
                    is_final=True,
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
