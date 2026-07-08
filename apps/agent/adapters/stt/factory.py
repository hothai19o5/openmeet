"""
STT Adapter Factory
Tạo adapter dựa trên config/env. Điểm duy nhất biết về tất cả implementations.
"""

import os
import logging

from ports.stt_port import STTPort

logger = logging.getLogger(__name__)


def create_stt_adapter(provider: str | None = None) -> STTPort:
    """
    Factory: tạo STT adapter dựa trên provider name.

    Args:
        provider: "local" | "openai" (hoặc None → đọc từ env STT_PROVIDER)

    Returns:
        Instance của STTPort implementation
    """
    provider = provider or os.getenv("STT_PROVIDER", "local")
    provider = provider.lower().strip()

    if provider == "local":
        from adapters.stt.local_whisper import LocalWhisperAdapter

        model_size = os.getenv("WHISPER_MODEL", "base")
        device = os.getenv("WHISPER_DEVICE", "cpu")
        logger.info(f"Creating LocalWhisperAdapter (model={model_size}, device={device})")
        return LocalWhisperAdapter(model_size=model_size, device=device)

    elif provider == "openai":
        from adapters.stt.openai_stt import OpenAISTTAdapter

        api_key = os.getenv("OPENAI_STT_API_KEY", "")
        base_url = os.getenv("OPENAI_STT_BASE_URL", "https://api.openai.com/v1")
        model = os.getenv("OPENAI_STT_MODEL", "whisper-1")

        if not api_key:
            raise ValueError("OPENAI_STT_API_KEY is required when STT_PROVIDER=openai")

        logger.info(f"Creating OpenAISTTAdapter (base_url={base_url}, model={model})")
        return OpenAISTTAdapter(api_key=api_key, base_url=base_url, model=model)

    elif provider == "groq":
        # Groq dùng OpenAI-compatible format nhưng base_url khác
        from adapters.stt.openai_stt import OpenAISTTAdapter

        api_key = os.getenv("GROQ_API_KEY", "")
        base_url = "https://api.groq.com/openai/v1"
        model = os.getenv("GROQ_STT_MODEL", "whisper-large-v3")

        if not api_key:
            raise ValueError("GROQ_API_KEY is required when STT_PROVIDER=groq")

        logger.info(f"Creating GroqSTTAdapter (model={model})")
        return OpenAISTTAdapter(api_key=api_key, base_url=base_url, model=model)

    else:
        raise ValueError(
            f"Unknown STT provider: '{provider}'. "
            f"Supported: local, openai, groq"
        )
