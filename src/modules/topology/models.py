from datetime import datetime, timezone
import enum
import uuid
from typing import Optional
from sqlmodel import Field, SQLModel, UniqueConstraint

class LocationType(str, enum.Enum):
    WAREHOUSE = "WAREHOUSE"
    BRANCH = "BRANCH"
    SECTOR = "SECTOR"
    ZONE = "ZONE"
    RACK = "RACK"
    LEVEL = "LEVEL"
    BIN = "BIN"
    CONSOLIDATION = "CONSOLIDATION"

class Location(SQLModel, table=True):
    __tablename__ = "locations"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_location_tenant_code"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True, nullable=False)
    parent_id: Optional[uuid.UUID] = Field(default=None, foreign_key="locations.id", nullable=True)
    code: str = Field(nullable=False, index=True)
    name: str = Field(nullable=False)
    location_type: LocationType = Field(nullable=False)
    stock_enabled: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )