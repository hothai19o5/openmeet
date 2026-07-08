"""
LLM Adapter Factory
Tạo adapter dựa trên config/env. Điểm duy nhất biết về tất cả implementations.
"""

import os
import logging

from ports.llm_port import LLMPort

logger = logging.getLogger(__name__)


def create_llm_adapter(provider: str | None = None) -> LLMPort:
    """
    Factory: tạo LLM adapter dựa trên provider name.

    Args:
        provider: "local" | "openai" | "groq" (hoặc None → đọc từ env LLM_PROVIDER)

    Returns:
        Instance của LLMPort implementation
    """
    provider = provider or os.getenv("LLM_PROVIDER", "openai")
    provider = provider.lower().strip()

    if provider == "local":
        from adapters.llm.local_ollama import LocalOllamaAdapter

        logger.info("Creating LocalOllamaAdapter")
        return LocalOllamaAdapter()

    elif provider == "openai":
        from adapters.llm.openai_llm import OpenAILLMAdapter

        api_key = os.getenv("OPENAI_LLM_API_KEY", os.getenv("OPENAI_API_KEY", ""))
        base_url = os.getenv("OPENAI_LLM_BASE_URL", "https://api.openai.com/v1")
        model = os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini")

        if not api_key:
            raise ValueError(
                "OPENAI_LLM_API_KEY (or OPENAI_API_KEY) is required when LLM_PROVIDER=openai"
            )

        logger.info(f"Creating OpenAILLMAdapter (base_url={base_url}, model={model})")
        return OpenAILLMAdapter(api_key=api_key, base_url=base_url, model=model)

    elif provider == "groq":
        # Groq dùng OpenAI-compatible format
        from adapters.llm.openai_llm import OpenAILLMAdapter

        api_key = os.getenv("GROQ_API_KEY", "")
        base_url = "https://api.groq.com/openai/v1"
        model = os.getenv("GROQ_LLM_MODEL", "llama-3.3-70b-versatile")

        if not api_key:
            raise ValueError("GROQ_API_KEY is required when LLM_PROVIDER=groq")

        logger.info(f"Creating GroqLLMAdapter (model={model})")
        return OpenAILLMAdapter(api_key=api_key, base_url=base_url, model=model)

    else:
        raise ValueError(
            f"Unknown LLM provider: '{provider}'. "
            f"Supported: local, openai, groq"
        )
