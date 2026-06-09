from fastapi import APIRouter
from pydantic import BaseModel
from app.services.groq_service import extract_user_intent

# Router banayenge jisko main.py me connect karenge
router = APIRouter()

# Schema for incoming request
class ChatRequest(BaseModel):
    user_input: str

@router.post("/extract-intent")
async def extract_intent_endpoint(request: ChatRequest):
    # Service layer se function call kiya
    return extract_user_intent(request.user_input)