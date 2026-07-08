"""
STT Adapter Factory
Tạo adapter dựa trên config/env. Điểm duy nhất biết về tất cả implementations.

Provider options:
  - "local"     → faster-whisper (Option A: CPU, nhẹ, không diarization)
  - "whisperx"  → whisperx + pyannote 3.1 (Option C: GPU, full diarization + word alignment)
  - "openai"    → OpenAI-compatible API (Option B: remote, không diarization)
  - "groq"      → Groq API (Option B variant: remote, nhanh, free tier)
"""

import os
import logging

from ports.stt_port import STTPort

logger = logging.getLogger(__name__)


def create_stt_adapter(provider: str | None = None) -> STTPort:
    """
    Factory: tạo STT adapter dựa trên provider name.

    Args:
        provider: "local" | "whisperx" | "openai" | "groq"
                  (hoặc None → đọc từ env STT_PROVIDER)

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

    elif provider == "whisperx":
        from adapters.stt.local_whisperx import LocalWhisperXAdapter

        model_size = os.getenv("WHISPERX_MODEL", "large-v3")
        device = os.getenv("WHISPERX_DEVICE", "cuda")
        compute_type = os.getenv("WHISPERX_COMPUTE_TYPE", None)
        hf_token = os.getenv("HF_TOKEN", "") or os.getenv("HUGGINGFACE_TOKEN", "")
        min_speakers = int(os.getenv("WHISPERX_MIN_SPEAKERS", "0")) or None
        max_speakers = int(os.getenv("WHISPERX_MAX_SPEAKERS", "0")) or None

        if not hf_token:
            logger.warning(
                "HF_TOKEN not set — diarization will be disabled. "
                "Accept license at: huggingface.co/pyannote/speaker-diarization-3.1"
            )

        logger.info(
            f"Creating LocalWhisperXAdapter (model={model_size}, device={device}, "
            f"compute={compute_type or 'auto'}, diarize={'yes' if hf_token else 'no'})"
        )
        return LocalWhisperXAdapter(
            model_size=model_size,
            device=device,
            compute_type=compute_type,
            hf_token=hf_token,
            min_speakers=min_speakers,
            max_speakers=max_speakers,
        )

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
            f"Supported: local, whisperx, openai, groq"
        )
