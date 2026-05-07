from pydantic import BaseModel, field_validator
from typing import Literal
from datetime import datetime


class JobCreate(BaseModel):
    customer_name: str
    location: str
    issue: str
    priority: Literal["High", "Medium", "Low"]

    @field_validator("customer_name", "location", "issue")
    @classmethod
    def field_must_not_be_empty(cls, value):
        if value is None or value.strip() == "":
            raise ValueError("Field cannot be empty")
        return value.strip()


class JobUpdate(BaseModel):
    customer_name: str
    location: str
    issue: str
    priority: Literal["High", "Medium", "Low"]
    status: Literal["pending", "inprogress", "completed"]

    @field_validator("customer_name", "location", "issue")
    @classmethod
    def field_must_not_be_empty(cls, value):
        if value is None or value.strip() == "":
            raise ValueError("Field cannot be empty")
        return value.strip()


class JobResponse(BaseModel):
    id: int
    customer_name: str
    location: str
    issue: str
    priority: str
    status: str
    is_deleted: bool
    is_saved: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True