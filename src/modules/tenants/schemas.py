from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict, Field

class TenantCreate(BaseModel):
    code: str = Field(..., min_length=3, max_length=50, example="FRANKMARC")
    name: str = Field(..., min_length=2, max_length=255, example="Frankmarc Chile S.A.")

class TenantResponse(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)