import uuid
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.middleware.tenant import get_tenant_db_session, oauth2_scheme
from src.core.security import decode_token
from src.modules.topology.models import LocationType
from src.modules.topology.schemas import LocationCreate, LocationResponse, LocationStockToggle
from src.modules.topology.service import TopologyService

router = APIRouter(prefix="/topology", tags=["Topología de Red (Bodegas & Ubicaciones)"])

@router.post("/locations", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    payload: LocationCreate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_tenant_db_session)
):
    tenant_id = uuid.UUID(decode_token(token).get("tenant_id"))
    return await TopologyService.create_location(db, tenant_id, payload)

@router.get("/locations", response_model=list[LocationResponse])
async def list_locations(
    location_type: Optional[LocationType] = Query(None),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_tenant_db_session)
):
    tenant_id = uuid.UUID(decode_token(token).get("tenant_id"))
    return await TopologyService.list_locations(db, tenant_id, location_type)

@router.patch("/locations/{location_id}/stock-toggle", response_model=LocationResponse)
async def toggle_stock_enabled(
    location_id: uuid.UUID,
    payload: LocationStockToggle,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_tenant_db_session)
):
    """Habilita o deshabilita la capacidad de almacenar stock en una sucursal/ubicación."""
    tenant_id = uuid.UUID(decode_token(token).get("tenant_id"))
    return await TopologyService.toggle_stock(db, tenant_id, location_id, payload)