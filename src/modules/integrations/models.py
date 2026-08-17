from datetime import datetime, timezone
import enum
import uuid
from typing import Any, Dict
from sqlmodel import Field, SQLModel
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

class EventType(str, enum.Enum):
    PRODUCT_SYNC = "PRODUCT_SYNC"
    STOCK_UPDATED = "STOCK_UPDATED"
    ORDER_CREATED = "ORDER_CREATED"
    ORDER_DISPATCHED = "ORDER_DISPATCHED"

class IntegrationStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class WebhookSubscription(SQLModel, table=True):
    __tablename__ = "webhook_subscriptions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True, nullable=False)
    target_url: str = Field(nullable=False)
    secret_key: str = Field(nullable=False)
    event_type: EventType = Field(nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )

class IntegrationEvent(SQLModel, table=True):
    __tablename__ = "integration_events"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True, nullable=False)
    event_type: EventType = Field(nullable=False, index=True)
    payload: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    status: IntegrationStatus = Field(default=IntegrationStatus.PENDING, nullable=False)
    error_message: str | None = Field(default=None, nullable=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )