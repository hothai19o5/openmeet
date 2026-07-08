"""
OpenAI-compatible LLM Adapter
Gọi OpenAI Chat Completions API (hoặc bất kỳ server nào tương thích: vLLM, LM Studio, Together, Groq, ...).

Endpoint: POST /v1/chat/completions
Format: { model, messages, temperature, max_tokens, stream }

Tương thích: OpenAI, Azure OpenAI, Groq, Together AI, vLLM, LM Studio, ...
"""

import os
import logging
import json
from typing import AsyncIterator

import httpx

from ports.llm_port import LLMPort, LLMResponse

logger = logging.getLogger(__name__)


class OpenAILLMAdapter(LLMPort):
    """
    Adapter thực thi LLMPort bằng OpenAI-compatible API.
    Dùng được cho: OpenAI, Groq, Together, vLLM, LM Studio, Azure OpenAI, ...
    """

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.openai.com/v1",
        model: str = "gpt-4o-mini",
    ):
        self.api_key = api_key or os.getenv("OPENAI_LLM_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=120.0,
        )

    def _build_messages(self, prompt: str, system_prompt: str) -> list[dict]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    async def complete(
        self,
        prompt: str,
        *,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Gọi OpenAI Chat Completions (non-streaming)."""
        payload = {
            "model": self.model,
            "messages": self._build_messages(prompt, system_prompt),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }

        response = await self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()

        choice = data.get("choices", [{}])[0]
        return LLMResponse(
            text=choice.get("message", {}).get("content", "").strip(),
            model=data.get("model", self.model),
            tokens_used=data.get("usage", {}).get("total_tokens"),
            finish_reason=choice.get("finish_reason"),
        )

    async def complete_stream(
        self,
        prompt: str,
        *,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """Streaming completion qua SSE (Server-Sent Events)."""
        payload = {
            "model": self.model,
            "messages": self._build_messages(prompt, system_prompt),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        async with self._client.stream("POST", "/chat/completions", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.startswith("data: "):
                    continue
                data_str = line[6:]
                if data_str.strip() == "[DONE]":
                    break
                chunk = json.loads(data_str)
                delta = chunk.get("choices", [{}])[0].get("delta", {})
                content = delta.get("content", "")
                if content:
                    yield content

    async def close(self) -> None:
        await self._client.aclose()
        logger.info("OpenAI LLM client closed.")
