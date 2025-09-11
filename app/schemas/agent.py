from pydantic import BaseModel

class AgentQuery(BaseModel):
    """Schema for the /ask request"""
    session_id: str
    question: str

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "7e05d582-6d6f-4ae4-b174-353a6f1f5d4f",
                "question": "What is Jorge's professional background?"
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
