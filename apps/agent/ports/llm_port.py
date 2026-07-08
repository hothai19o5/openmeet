# OpenMeet AI Agent - LLM Port (Protocol)

from abc import ABC, abstractmethod
from typing import AsyncIterator
from dataclasses import dataclass


@dataclass
class LLMResponse:
    """Kết quả từ LLM."""
    text: str
    model: str = ""
    tokens_used: int | None = None
    finish_reason: str | None = None


class LLMPort(ABC):
    """
    Port (Protocol) cho Large Language Model.
    Mọi adapter (local Ollama, OpenAI, Groq, vLLM, ...) phải implement interface này.
    """

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        *,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """
        Sinh text từ prompt.

        Args:
            prompt: Câu lệnh của người dùng
            system_prompt: System prompt (role instruction)
            temperature: Độ ngẫu nhiên (0-1)
            max_tokens: Số token tối đa

        Returns:
            LLMResponse với text đã sinh
        """
        ...

    @abstractmethod
    async def complete_stream(
        self,
        prompt: str,
        *,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """
        Streaming completion cho real-time output.

        Yields:
            Token chunks (str)
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """Giải phóng tài nguyên."""
        ...
