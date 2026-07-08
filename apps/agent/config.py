"""
Config loader — đọc config từ env vars.
"""

import os
from dataclasses import dataclass


@dataclass
class AgentConfig:
    """Cấu hình runtime cho AI Agent."""

    # Provider selection
    stt_provider: str = "local"
    llm_provider: str = "openai"

    # STT: Local Whisper (Option A — faster-whisper, no diarization)
    whisper_model: str = "base"
    whisper_device: str = "cpu"

    # STT: WhisperX (Option C — full diarization + word alignment)
    whisperx_model: str = "large-v3"
    whisperx_device: str = "cuda"
    whisperx_compute_type: str = ""
    hf_token: str = ""
    whisperx_min_speakers: int | None = None
    whisperx_max_speakers: int | None = None

    # STT: OpenAI-compatible
    openai_stt_api_key: str = ""
    openai_stt_base_url: str = "https://api.openai.com/v1"
    openai_stt_model: str = "whisper-1"

    # LLM: Local Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # LLM: OpenAI-compatible
    openai_llm_api_key: str = ""
    openai_llm_base_url: str = "https://api.openai.com/v1"
    openai_llm_model: str = "gpt-4o-mini"

    # LiveKit
    livekit_url: str = "ws://localhost:7880"
    livekit_api_key: str = "devkey"
    livekit_api_secret: str = ""

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Load config từ environment variables."""
        return cls(
            stt_provider=os.getenv("STT_PROVIDER", "local"),
            llm_provider=os.getenv("LLM_PROVIDER", "openai"),
            whisper_model=os.getenv("WHISPER_MODEL", "base"),
            whisper_device=os.getenv("WHISPER_DEVICE", "cpu"),
            whisperx_model=os.getenv("WHISPERX_MODEL", "large-v3"),
            whisperx_device=os.getenv("WHISPERX_DEVICE", "cuda"),
            whisperx_compute_type=os.getenv("WHISPERX_COMPUTE_TYPE", ""),
            hf_token=os.getenv("HF_TOKEN", os.getenv("HUGGINGFACE_TOKEN", "")),
            whisperx_min_speakers=int(os.getenv("WHISPERX_MIN_SPEAKERS", "0")) or None,
            whisperx_max_speakers=int(os.getenv("WHISPERX_MAX_SPEAKERS", "0")) or None,
            openai_stt_api_key=os.getenv("OPENAI_STT_API_KEY", ""),
            openai_stt_base_url=os.getenv("OPENAI_STT_BASE_URL", "https://api.openai.com/v1"),
            openai_stt_model=os.getenv("OPENAI_STT_MODEL", "whisper-1"),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2"),
            openai_llm_api_key=os.getenv("OPENAI_LLM_API_KEY", os.getenv("OPENAI_API_KEY", "")),
            openai_llm_base_url=os.getenv("OPENAI_LLM_BASE_URL", "https://api.openai.com/v1"),
            openai_llm_model=os.getenv("OPENAI_LLM_MODEL", "gpt-4o-mini"),
            livekit_url=os.getenv("LIVEKIT_URL", "ws://localhost:7880"),
            livekit_api_key=os.getenv("LIVEKIT_API_KEY", "devkey"),
            livekit_api_secret=os.getenv("LIVEKIT_API_SECRET", ""),
        )