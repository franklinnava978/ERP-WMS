import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.middleware.tenant import get_tenant_db_session, oauth2_scheme
from src.core.security import decode_token
from src.modules.inventory.schemas import StockMoveRequest, StockResponse, InventoryLogResponse
from src.modules.inventory.service import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventario & Movimientos (PDA)"])

@router.post("/movements", response_model=InventoryLogResponse, status_code=status.HTTP_201_CREATED)
async def process_movement(
    payload: StockMoveRequest,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_tenant_db_session)
):
    """Procesa ingresos, salidas o transferencias entre ubicaciones/LPNs con idempotencia."""
    tenant_id = uuid.UUID(decode_token(token).get("tenant_id"))
    return await InventoryService.move_stock(db, tenant_id, payload)

@router.get("/stock/location/{location_id}", response_model=list[StockResponse])
async def get_stock_by_location(
    location_id: uuid.UUID,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_tenant_db_session)
):
    """Consulta las existencias disponibles y reservadas en una ubicación."""
    tenant_id = uuid.UUID(decode_token(token).get("tenant_id"))
    return await InventoryService.get_stock_by_location(db, tenant_id, location_id)