from datetime import datetime, timezone
import enum
import uuid
from typing import Optional
from sqlmodel import Field, SQLModel, UniqueConstraint

class MovementType(str, enum.Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"
    TRANSFER = "TRANSFER"
    RESERVE = "RESERVE"
    UNRESERVE = "UNRESERVE"
    ADJUSTMENT = "ADJUSTMENT"

class Stock(SQLModel, table=True):
    __tablename__ = "stock"
    __table_args__ = (
        UniqueConstraint("tenant_id", "location_id", "product_id", "lpn_code", name="uq_stock_item"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True, nullable=False)
    location_id: uuid.UUID = Field(foreign_key="locations.id", index=True, nullable=False)
    product_id: uuid.UUID = Field(foreign_key="products.id", index=True, nullable=False)
    lpn_code: Optional[str] = Field(default=None, index=True, nullable=True)  # Contenedor / Pallet
    quantity_available: float = Field(default=0.0, nullable=False)
    quantity_reserved: float = Field(default=0.0, nullable=False)
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )

class InventoryLog(SQLModel, table=True):
    __tablename__ = "inventory_logs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True, nullable=False)
    product_id: uuid.UUID = Field(foreign_key="products.id", index=True, nullable=False)
    origin_location_id: Optional[uuid.UUID] = Field(default=None, foreign_key="locations.id", nullable=True)
    destination_location_id: Optional[uuid.UUID] = Field(default=None, foreign_key="locations.id", nullable=True)
    lpn_code: Optional[str] = Field(default=None, nullable=True)
    movement_type: MovementType = Field(nullable=False)
    quantity: float = Field(nullable=False)
    idempotency_key: str = Field(unique=True, index=True, nullable=False)  # Evita duplicados PDA
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )