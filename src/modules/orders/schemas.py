from datetime import datetime
import uuid
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from src.modules.orders.models import OrderStatus

class OrderItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity_requested: float = Field(..., gt=0, example=10.0)

class OrderCreate(BaseModel):
    order_number: str = Field(..., min_length=3, max_length=50, example="PED-2026-001")
    customer_name: str = Field(..., min_length=2, max_length=255, example="Constructora El Sol")
    location_id: uuid.UUID
    items: List[OrderItemCreate]

class OrderItemResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    quantity_requested: float
    quantity_reserved: float

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    order_number: str
    customer_name: str
    location_id: uuid.UUID
    status: OrderStatus
    created_at: datetime
    items: List[OrderItemResponse] = []

    model_config = ConfigDict(from_attributes=True)