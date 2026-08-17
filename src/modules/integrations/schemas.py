from datetime import datetime
import uuid
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from src.modules.integrations.models import EventType, IntegrationStatus

class WebhookCreate(BaseModel):
    target_url: HttpUrl = Field(..., description="URL destino para enviar el payload vía POST")
    secret_key: str = Field(..., min_length=8, description="Llave para firmar el payload (HMAC)")
    event_type: EventType

class WebhookResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    target_url: HttpUrl
    event_type: EventType
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class EventResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    event_type: EventType
    payload: Dict[str, Any]
    status: IntegrationStatus
    error_message: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)