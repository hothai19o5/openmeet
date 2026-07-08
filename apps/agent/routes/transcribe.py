"""
Transcribe endpoints: POST /api/transcribe (batch) + WS /api/transcribe/stream (real-time)
"""

import logging
from fastapi import APIRouter, Request, UploadFile, File, WebSocket, WebSocketDisconnect

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/transcribe")
async def transcribe(
    request: Request,
    file: UploadFile = File(...),
    language: str = "vi",
):
    """
    Batch transcription: upload audio file → nhận text.
    Hỗ trợ WAV, MP3, WebM, OGG, ...
    """
    stt = request.app.state.stt
    audio_data = await file.read()
    result = await stt.transcribe(audio_data, language=language)
    return {
        "text": result.text,
        "language": result.language,
        "is_final": result.is_final,
    }


@router.websocket("/transcribe/stream")
async def transcribe_stream(
    websocket: WebSocket,
):
    """
    Real-time streaming transcription qua WebSocket.
    Client gửi binary audio chunks (PCM 16kHz 16-bit mono).
    Server yield JSON transcription segments.
    """
    await websocket.accept()
    stt = websocket.app.state.stt  # type: ignore

    async def audio_stream():
        try:
            while True:
                data = await websocket.receive_bytes()
                if data == b"STOP":
                    break
                yield data
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected from transcribe stream.")
            return

    try:
        async for result in stt.transcribe_stream(audio_stream(), language="vi"):
            import json
            await websocket.send_json({
                "text": result.text,
                "language": result.language,
                "is_final": result.is_final,
                "segment_id": result.segment_id,
            })
    except WebSocketDisconnect:
        logger.info("Client disconnected during transcription.")
    except Exception as e:
        logger.error(f"Transcribe stream error: {e}")
        await websocket.close(code=1011, reason=str(e))
