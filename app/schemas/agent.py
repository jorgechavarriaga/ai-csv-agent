from pydantic import BaseModel
from typing import Optional


class AgentQuery(BaseModel):
    """Schema for the /ask request"""
    session_id: str
    question: str
    language: Optional[str] = "en" 

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "7e05d582-6d6f-4ae4-b174-353a6f1f5d4f",
                "question": "What is Jorge's professional background?",
                "language": "en"
            }
        }


class AgentAnswer(BaseModel):
    """Schema for the /ask success data"""
    question: str
    answer: str

class AgentResponse(BaseModel):
    """Typed success response for /ask endpoint"""
    status: str = "success"
    data: AgentAnswer
