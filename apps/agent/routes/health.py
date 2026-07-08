"""
Health check endpoint
"""

from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/health")
async def health(request: Request):
    """Health check — trả về trạng thái adapters."""
    return {
        "status": "ok",
        "stt_provider": request.app.state.stt.__class__.__name__,
        "llm_provider": request.app.state.llm.__class__.__name__,
    }
