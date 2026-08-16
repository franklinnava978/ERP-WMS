from datetime import datetime, timezone
import uuid
from typing import Optional
from sqlmodel import Field, SQLModel, UniqueConstraint

class UnitOfMeasure(SQLModel, table=True):
    __tablename__ = "units_of_measure"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_uom_tenant_code"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True, nullable=False)
    code: str = Field(nullable=False)  # Ej: "CAJA", "M2", "PALLET", "UN"
    name: str = Field(nullable=False)  # Ej: "Caja", "Metro Cuadrado"

class Product(SQLModel, table=True):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("tenant_id", "sku", name="uq_product_tenant_sku"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True, nullable=False)
    sku: str = Field(nullable=False, index=True)
    name: str = Field(nullable=False)
    inventory_uom_id: uuid.UUID = Field(foreign_key="units_of_measure.id", nullable=False)
    valuation_uom_id: uuid.UUID = Field(foreign_key="units_of_measure.id", nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )

class UOMConversion(SQLModel, table=True):
    __tablename__ = "uom_conversions"
    __table_args__ = (
        UniqueConstraint("tenant_id", "product_id", "from_uom_id", "to_uom_id", name="uq_uom_conversion"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    tenant_id: uuid.UUID = Field(foreign_key="tenants.id", index=True, nullable=False)
    product_id: uuid.UUID = Field(foreign_key="products.id", index=True, nullable=False)
    from_uom_id: uuid.UUID = Field(foreign_key="units_of_measure.id", nullable=False)
    to_uom_id: uuid.UUID = Field(foreign_key="units_of_measure.id", nullable=False)
    conversion_factor: float = Field(nullable=False)  # Ej: 1 CAJA -> 2.45 M2 (Factor = 2.45)