"""
Local Ollama LLM Adapter
Gọi Ollama REST API (http://localhost:11434) — chạy LLM local, không cần API key.

Ollama REST API: POST /api/chat
"""

import os
import logging
from typing import AsyncIterator

import httpx

from ports.llm_port import LLMPort, LLMResponse

logger = logging.getLogger(__name__)


class LocalOllamaAdapter(LLMPort):
    """
    Adapter thực thi LLMPort bằng Ollama REST API.
    Chạy hoàn toàn local, không cần Internet, không cần API key.
    """

    def __init__(
        self,
        base_url: str | None = None,
        model: str | None = None,
    ):
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2")
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=120.0)

    async def complete(
        self,
        prompt: str,
        *,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> LLMResponse:
        """Gọi Ollama /api/chat."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        response = await self._client.post("/api/chat", json=payload)
        response.raise_for_status()
        data = response.json()

        return LLMResponse(
            text=data.get("message", {}).get("content", "").strip(),
            model=self.model,
            tokens_used=data.get("eval_count"),
            finish_reason="stop" if data.get("done") else None,
        )

    async def complete_stream(
        self,
        prompt: str,
        *,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> AsyncIterator[str]:
        """Streaming completion qua Ollama NDJSON stream."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }

        async with self._client.stream("POST", "/api/chat", json=payload) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line.strip():
                    continue
                import json
                chunk = json.loads(line)
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content
                if chunk.get("done"):
                    break

    async def close(self) -> None:
        await self._client.aclose()
        logger.info("Ollama LLM client closed.")
