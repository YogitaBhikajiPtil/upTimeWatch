import re
from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, Field, PlainSerializer, field_validator

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Datetimes are stored as naive UTC; send them as ISO strings ending in "Z"
UTCDatetime = Annotated[
    datetime, PlainSerializer(lambda d: d.isoformat() + "Z", return_type=str, when_used="json")
]


class Credentials(BaseModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=64)

    @field_validator("email")
    @classmethod
    def check_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not EMAIL_RE.match(v):
            raise ValueError("Invalid email address")
        return v


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: str

    model_config = {"from_attributes": True}


class MonitorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    url: str = Field(max_length=2048)
    interval_seconds: int = Field(default=60, ge=30, le=3600)


class MonitorUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    interval_seconds: Optional[int] = Field(default=None, ge=30, le=3600)
    is_active: Optional[bool] = None


class MonitorOut(BaseModel):
    id: int
    name: str
    url: str
    interval_seconds: int
    is_active: bool
    status: str
    last_checked_at: Optional[UTCDatetime] = None
    last_status_code: Optional[int] = None
    last_response_ms: Optional[int] = None
    uptime_24h: Optional[float] = None  # percentage, None if no checks yet

    model_config = {"from_attributes": True}


class ResultOut(BaseModel):
    id: int
    checked_at: UTCDatetime
    is_up: bool
    status_code: Optional[int] = None
    response_ms: Optional[int] = None
    error: Optional[str] = None

    model_config = {"from_attributes": True}
