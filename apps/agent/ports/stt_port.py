# OpenMeet AI Agent - STT Port (Protocol)

from abc import ABC, abstractmethod
from typing import AsyncIterator
from dataclasses import dataclass


@dataclass
class TranscriptionResult:
    """Kết quả chuyển đổi giọng nói thành văn bản."""
    text: str
    language: str | None = None
    confidence: float | None = None
    is_final: bool = True
    segment_id: int = 0


class STTPort(ABC):
    """
    Port (Protocol) cho Speech-to-Text.
    Mọi adapter (local Whisper, OpenAI, Groq, ...) phải implement interface này.
    """

    @abstractmethod
    async def transcribe(
        self, audio_data: bytes, *, language: str = "vi", sample_rate: int = 16000
    ) -> TranscriptionResult:
        """
        Chuyển đổi audio bytes thành text.

        Args:
            audio_data: Raw audio bytes (WAV/PCM/WebM)
            language: Mã ngôn ngữ (vi, en, ja, ...)
            sample_rate: Tần số mẫu (Hz)

        Returns:
            TranscriptionResult với text đã được chuyển đổi
        """
        ...

    @abstractmethod
    async def transcribe_stream(
        self, audio_stream: AsyncIterator[bytes], *, language: str = "vi"
    ) -> AsyncIterator[TranscriptionResult]:
        """
        Streaming transcription cho real-time use case.

        Args:
            audio_stream: Async iterator yielding audio chunks
            language: Mã ngôn ngữ

        Yields:
            TranscriptionResult cho mỗi segment
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """Giải phóng tài nguyên."""
        ...
