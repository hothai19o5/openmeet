"""
Summarize endpoint: POST /api/summarize
Tóm tắt văn bản (transcript cuộc họp) bằng LLM.
"""

import logging
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter()
logger = logging.getLogger(__name__)

# System prompt mặc định cho tóm tắt cuộc họp
DEFAULT_SYSTEM_PROMPT = """Bạn là trợ lý AI chuyên tóm tắt cuộc họp.
Hãy tóm tắt nội dung cuộc họp một cách súc tích, rõ ràng.

Nếu transcript có speaker tags (SPEAKER_00, SPEAKER_01, ...), hãy:
- Gán action items cho đúng speaker
- Phân biệt ý kiến của từng người tham gia
- Liệt kê người tham gia ở đầu bản tóm tắt

Format đầu ra:
1. **Người tham gia**: Danh sách speaker (nếu có)
2. **Điểm chính**: Các vấn đề đã thảo luận
3. **Quyết định**: Các quyết định đã thống nhất
4. **Action items**: Việc cần làm + người phụ trách (nếu có speaker info)

Trả lời bằng tiếng Việt."""


class SummarizeRequest(BaseModel):
    """Request body cho endpoint /summarize."""
    text: str = Field(..., description="Văn bản cần tóm tắt (transcript cuộc họp)")
    # Optional: structured segments (nếu client có diarization data)
    segments: list[dict] | None = Field(
        default=None,
        description="Structured transcript: [{\"text\": \"...\", \"speaker\": \"SPEAKER_00\", \"start_time\": 1.2, \"end_time\": 3.5}]"
    )
    system_prompt: str = Field(default=DEFAULT_SYSTEM_PROMPT, description="System prompt tùy chỉnh")
    temperature: float = Field(default=0.3, ge=0.0, le=1.0, description="Độ ngẫu nhiên")
    max_tokens: int = Field(default=1024, ge=100, le=4096, description="Số token tối đa")


class SummarizeResponse(BaseModel):
    """Response body cho endpoint /summarize."""
    summary: str
    model: str
    tokens_used: int | None = None


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: Request, body: SummarizeRequest):
    """
    Tóm tắt văn bản bằng LLM adapter đang được cấu hình.
    """
    llm = request.app.state.llm

    # Build prompt: nếu client gửi structured segments, format với speaker tags
    if body.segments:
        lines = []
        for seg in body.segments:
            speaker_tag = f"[{seg.get('speaker', '')}]" if seg.get("speaker") else ""
            time_tag = f"[{seg.get('start_time', 0):.1f}-{seg.get('end_time', 0):.1f}s]"
            lines.append(f"{time_tag} {speaker_tag} {seg.get('text', '')}".strip())
        transcript_text = "\n".join(lines)
    else:
        transcript_text = body.text

    prompt = f"Hãy tóm tắt nội dung sau:\n\n{transcript_text}"

    result = await llm.complete(
        prompt=prompt,
        system_prompt=body.system_prompt,
        temperature=body.temperature,
        max_tokens=body.max_tokens,
    )

    return SummarizeResponse(
        summary=result.text,
        model=result.model,
        tokens_used=result.tokens_used,
    )
