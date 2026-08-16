from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    tenant_id: uuid.UUID
    email: EmailStr
    password: str = Field(..., min_length=8, example="Password123!")
    full_name: str = Field(..., min_length=2, max_length=255, example="Juan Pérez")

class LoginRequest(BaseModel):
    tenant_code: str = Field(..., example="FRANKMARC")
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tenant_id: uuid.UUID
    user_id: uuid.UUID

class UserResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)