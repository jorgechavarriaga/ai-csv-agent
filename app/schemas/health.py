from pydantic import BaseModel

class HealthData(BaseModel):
    """Schema for health data inside success response"""
    status: str

class HealthResponse(BaseModel):
    """Typed response for health endpoint"""
    status: str = "success"
    data: HealthData
