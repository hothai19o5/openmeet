# OpenMeet AI Agent - STT Port (Protocol)

from abc import ABC, abstractmethod
from typing import AsyncIterator
from dataclasses import dataclass, field


@dataclass
class TranscriptionSegment:
    """Một đoạn text với speaker + timestamps (diarization)."""
    text: str
    speaker: str | None = None       # "SPEAKER_00", "SPEAKER_01", ... hoặc None nếu không có diarization
    start_time: float = 0.0          # seconds
    end_time: float = 0.0            # seconds
    confidence: float | None = None

    def format_for_llm(self) -> str:
        """Format segment cho LLM prompt (meeting transcript style)."""
        speaker_tag = f"[{self.speaker}]" if self.speaker else ""
        time_tag = f"[{self.start_time:.1f}-{self.end_time:.1f}s]"
        return f"{time_tag} {speaker_tag} {self.text}".strip()


@dataclass
class TranscriptionResult:
    """Kết quả chuyển đổi giọng nói thành văn bản."""
    text: str
    language: str | None = None
    confidence: float | None = None
    is_final: bool = True
    segment_id: int = 0
    # Diarization fields — populated khi adapter hỗ trợ speaker recognition
    speaker: str | None = None
    start_time: float = 0.0
    end_time: float = 0.0
    segments: list[TranscriptionSegment] = field(default_factory=list)

    def format_for_llm(self) -> str:
        """Format toàn bộ result thành transcript cho LLM (summarize)."""
        if self.segments:
            return "\n".join(seg.format_for_llm() for seg in self.segments)
        return self.text


class STTPort(ABC):
    """
    Port (Protocol) cho Speech-to-Text.
    Mọi adapter (local Whisper, WhisperX, OpenAI, Groq, ...) phải implement interface này.

    Diarization support:
    - Adapter KHÔNG hỗ trợ diarization: speaker=None, segments=[]
    - Adapter CÓ hỗ trợ diarization (WhisperX): speaker + segments populated
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
            TranscriptionResult với text, segments (nếu có diarization), speaker info
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

    @property
    def supports_diarization(self) -> bool:
        """True nếu adapter hỗ trợ speaker diarization."""
        return False
