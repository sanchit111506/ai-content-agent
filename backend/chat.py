from fastapi import APIRouter
from pydantic import BaseModel

from agents.orchestrator import generate_content


router = APIRouter()


class ChatRequest(BaseModel):
    prompt: str


@router.post("/chat")
def chat(request: ChatRequest):

    result = generate_content(request.prompt)

    return {
        "prompt": request.prompt,
        "response": str(result)
    }