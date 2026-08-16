from datetime import datetime
import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

# Unidades de Medida
class UOMCreate(BaseModel):
    code: str = Field(..., min_length=1, max_length=20, example="CAJA")
    name: str = Field(..., min_length=1, max_length=100, example="Caja")

class UOMResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    code: str
    name: str

    model_config = ConfigDict(from_attributes=True)

# Productos
class ProductCreate(BaseModel):
    sku: str = Field(..., min_length=1, max_length=100, example="CER-PORC-60X60")
    name: str = Field(..., min_length=1, max_length=255, example="Porcelanato 60x60 Beige")
    inventory_uom_id: uuid.UUID
    valuation_uom_id: uuid.UUID

class ProductResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    sku: str
    name: str
    inventory_uom_id: uuid.UUID
    valuation_uom_id: uuid.UUID
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Conversiones UOM
class UOMConversionCreate(BaseModel):
    product_id: uuid.UUID
    from_uom_id: uuid.UUID
    to_uom_id: uuid.UUID
    conversion_factor: float = Field(..., gt=0, example=2.44)

class UOMConversionResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    product_id: uuid.UUID
    from_uom_id: uuid.UUID
    to_uom_id: uuid.UUID
    conversion_factor: float

    model_config = ConfigDict(from_attributes=True)