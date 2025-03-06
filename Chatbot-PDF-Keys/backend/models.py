from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Message(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None

class ChatSession(BaseModel):
    session_id: str
    pdf_name: Optional[str] = None
    created_at: Optional[datetime] = None

class ChatHistory(BaseModel):
    session_id: str
    messages: List[Message]

class SummarizeRequest(BaseModel):
    pdf_content: str
    session_id: str
    pdf_name: Optional[str] = None

class ChatRequest(BaseModel):
    session_id: str
    message: str 