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

    # STT: Local Whisper
    whisper_model: str = "base"
    whisper_device: str = "cpu"

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