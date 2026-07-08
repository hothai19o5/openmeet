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
Bao gồm:
1. Các điểm chính đã thảo luận
2. Quyết định đã đưa ra
3. Công việc cần làm (action items)

Trả lời bằng tiếng Việt."""


class SummarizeRequest(BaseModel):
    """Request body cho endpoint /summarize."""
    text: str = Field(..., description="Văn bản cần tóm tắt (transcript cuộc họp)")
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

    # Tạo user prompt
    prompt = f"Hãy tóm tắt nội dung sau:\n\n{body.text}"

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
