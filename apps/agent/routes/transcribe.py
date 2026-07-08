"""
Transcribe endpoints: POST /api/transcribe (batch) + WS /api/transcribe/stream (real-time)

Response format:
  - Nếu adapter có diarization (whisperx): trả segments với speaker tags
  - Nếu không (faster-whisper, openai API): trả segments với speaker=null
"""

import logging
from fastapi import APIRouter, Request, UploadFile, File, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)


class SegmentOut(BaseModel):
    """Segment trong response JSON."""
    text: str
    speaker: str | None = None
    start_time: float = 0.0
    end_time: float = 0.0


class TranscribeResponse(BaseModel):
    """Response cho POST /api/transcribe."""
    text: str
    language: str | None = None
    speaker: str | None = None
    start_time: float = 0.0
    end_time: float = 0.0
    segments: list[SegmentOut] = []
    diarization: bool = False


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(
    request: Request,
    file: UploadFile = File(...),
    language: str = "vi",
):
    """
    Batch transcription: upload audio file → nhận text + speaker segments.

    Response phụ thuộc vào STT provider:
    - local (faster-whisper): text + timestamps, không có speaker
    - whisperx: text + timestamps + speaker tags (diarization)
    - openai/groq: text + timestamps (verbose_json), không có speaker
    """
    stt = request.app.state.stt
    audio_data = await file.read()
    result = await stt.transcribe(audio_data, language=language)

    return TranscribeResponse(
        text=result.text,
        language=result.language,
        speaker=result.speaker,
        start_time=result.start_time,
        end_time=result.end_time,
        segments=[
            SegmentOut(
                text=seg.text,
                speaker=seg.speaker,
                start_time=seg.start_time,
                end_time=seg.end_time,
            )
            for seg in result.segments
        ],
        diarization=stt.supports_diarization,
    )


@router.websocket("/transcribe/stream")
async def transcribe_stream(
    websocket: WebSocket,
):
    """
    Real-time streaming transcription qua WebSocket.
    Client gửi binary audio chunks (PCM 16kHz 16-bit mono).
    Server yield JSON transcription segments.

    Mỗi message JSON chứa:
    {
        "text": "...",
        "language": "vi",
        "is_final": false,
        "segment_id": 0,
        "speaker": "SPEAKER_00" | null,
        "start_time": 1.2,
        "end_time": 3.5,
        "segments": [{"text": "...", "speaker": "SPEAKER_00", "start_time": 1.2, "end_time": 3.5}],
        "diarization": true | false
    }
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
            await websocket.send_json({
                "text": result.text,
                "language": result.language,
                "is_final": result.is_final,
                "segment_id": result.segment_id,
                "speaker": result.speaker,
                "start_time": result.start_time,
                "end_time": result.end_time,
                "segments": [
                    {
                        "text": seg.text,
                        "speaker": seg.speaker,
                        "start_time": seg.start_time,
                        "end_time": seg.end_time,
                    }
                    for seg in result.segments
                ],
                "diarization": stt.supports_diarization,
            })
    except WebSocketDisconnect:
        logger.info("Client disconnected during transcription.")
    except Exception as e:
        logger.error(f"Transcribe stream error: {e}")
        await websocket.close(code=1011, reason=str(e))
