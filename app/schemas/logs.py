from pydantic import BaseModel
from typing import List

class LogEntry(BaseModel):
    """Schema for a single log entry"""
    id: int
    question: str
    answer: str
    ip_address: str
    created_at: str


class LogsResponse(BaseModel):
    """Typed response for logs endpoint"""
    status: str = "success"
    data: dict[str, List[LogEntry]]
