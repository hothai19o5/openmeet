"""
OpenMeet AI Agent - Main FastAPI Application

Architecture: Port-Adapter (Hexagonal) Pattern
- STT port: Speech-to-Text abstraction (local Whisper hoặc OpenAI-compatible API)
- LLM port: Large Language Model abstraction (local Ollama hoặc OpenAI-compatible API)
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from adapters.stt.factory import create_stt_adapter
from adapters.llm.factory import create_llm_adapter
from routes import transcribe, summarize, health

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Khởi tạo adapters khi app start, cleanup khi shutdown."""
    # Tạo STT adapter dựa trên config
    stt_provider = os.getenv("STT_PROVIDER", "local")
    app.state.stt = create_stt_adapter(stt_provider)
    logger.info(f"STT adapter initialized: {stt_provider}")

    # Tạo LLM adapter dựa trên config
    llm_provider = os.getenv("LLM_PROVIDER", "openai")
    app.state.llm = create_llm_adapter(llm_provider)
    logger.info(f"LLM adapter initialized: {llm_provider}")

    yield

    # Cleanup
    if hasattr(app.state.stt, "close"):
        await app.state.stt.close()
    if hasattr(app.state.llm, "close"):
        await app.state.llm.close()
    logger.info("Adapters cleaned up")


app = FastAPI(
    title="OpenMeet AI Agent",
    description="Speech-to-Text + LLM service với Port-Adapter architecture",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS cho frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict to OpenMeet domain trong production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(transcribe.router, prefix="/api", tags=["transcribe"])
app.include_router(summarize.router, prefix="/api", tags=["summarize"])
