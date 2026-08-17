from datetime import datetime, timezone
import enum
import uuid
from typing import Optional, List
from sqlmodel import Field, SQLModel, UniqueConstraint, Relationship

class OrderStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    RESERVED = "RESERVED"
    IN_PICKING = "IN_PICKING"
    PICKED = "PICKED"
    DISPATCHED = "DISPATCHED"
    CANCELLED = "CANCELLED"

class Order(SQLModel, table=True):
    __tablename__ = "orders"
    __table_args__ = (
        UniqueConstraint("tenant_id", "order_number", name="uq_orders_tenant_number"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True, nullable=False)
    order_number: str = Field(nullable=False, index=True)
    customer_name: str = Field(nullable=False)
    location_id: uuid.UUID = Field(foreign_key="locations.id", nullable=False)
    status: OrderStatus = Field(default=OrderStatus.DRAFT, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    items: List["OrderItem"] = Relationship(back_populates="order")

class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True, nullable=False)
    order_id: uuid.UUID = Field(foreign_key="orders.id", index=True, nullable=False)
    product_id: uuid.UUID = Field(foreign_key="products.id", nullable=False)
    quantity_requested: float = Field(nullable=False)
    quantity_reserved: float = Field(default=0.0, nullable=False)

    order: Optional[Order] = Relationship(back_populates="items")