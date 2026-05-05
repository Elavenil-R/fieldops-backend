from pydantic import BaseModel
from typing import Literal
from datetime import datetime


class JobCreate(BaseModel):
    customer_name: str
    location: str
    issue: str
    priority: Literal["High", "Medium", "Low"]


class JobResponse(BaseModel):
    id: int
    customer_name: str
    location: str
    issue: str
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  