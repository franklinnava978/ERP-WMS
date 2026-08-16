from datetime import datetime
import uuid
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from src.modules.topology.models import LocationType

class LocationCreate(BaseModel):
    parent_id: Optional[uuid.UUID] = None
    code: str = Field(..., min_length=2, max_length=100, example="CENTRO-01")
    name: str = Field(..., min_length=2, max_length=255, example="Bodega Central Santiago")
    location_type: LocationType = Field(..., example=LocationType.WAREHOUSE)
    stock_enabled: bool = Field(default=True, example=True)

class LocationStockToggle(BaseModel):
    stock_enabled: bool = Field(..., example=True)

class LocationResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    parent_id: Optional[uuid.UUID]
    code: str
    name: str
    location_type: LocationType
    stock_enabled: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)