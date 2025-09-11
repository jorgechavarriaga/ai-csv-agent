from pydantic import BaseModel

class AgentQuery(BaseModel):
    """Schema for the /ask request"""
    question: str

    class Config:
        json_schema_extra = {
            "example": {
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
