from datetime import datetime
import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from src.modules.inventory.models import MovementType

class StockMoveRequest(BaseModel):
    idempotency_key: str = Field(..., description="UUID o clave de idempotencia generada por el PDA Zebra")
    product_id: uuid.UUID
    origin_location_id: Optional[uuid.UUID] = None
    destination_location_id: Optional[uuid.UUID] = None
    lpn_code: Optional[str] = Field(default=None, example="LPN-2026-0001")
    quantity: float = Field(..., gt=0)

class StockReserveRequest(BaseModel):
    idempotency_key: str
    product_id: uuid.UUID
    location_id: uuid.UUID
    lpn_code: Optional[str] = None
    quantity: float = Field(..., gt=0)

class StockResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    location_id: uuid.UUID
    product_id: uuid.UUID
    lpn_code: Optional[str]
    quantity_available: float
    quantity_reserved: float
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InventoryLogResponse(BaseModel):
    id: uuid.UUID
    movement_type: MovementType
    quantity: float
    idempotency_key: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)