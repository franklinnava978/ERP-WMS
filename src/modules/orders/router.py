import uuid
from fastapi import APIRouter, Depends, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.middleware.tenant import get_tenant_db_session, oauth2_scheme
from src.core.security import decode_token
from src.modules.orders.schemas import OrderCreate, OrderResponse
from src.modules.orders.service import OrderService

router = APIRouter(prefix="/orders", tags=["Pedidos & Despachos"])

@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: OrderCreate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_tenant_db_session)
):
    """Crea una nueva orden de venta/despacho en estado DRAFT."""
    tenant_id = uuid.UUID(decode_token(token).get("tenant_id"))
    return await OrderService.create_order(db, tenant_id, payload)

@router.post("/{order_id}/reserve", response_model=OrderResponse)
async def reserve_order_stock(
    order_id: uuid.UUID,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_tenant_db_session)
):
    """Reserva automáticamente el stock disponible en bodega para la orden."""
    tenant_id = uuid.UUID(decode_token(token).get("tenant_id"))
    return await OrderService.reserve_stock_for_order(db, tenant_id, order_id)

@router.post("/{order_id}/dispatch", response_model=OrderResponse)
async def dispatch_order(
    order_id: uuid.UUID,
    x_idempotency_key: str = Header(..., alias="X-Idempotency-Key"),
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_tenant_db_session)
):
    """Confirma el despacho del pedido y descuenta definitivamente la reserva de inventario."""
    tenant_id = uuid.UUID(decode_token(token).get("tenant_id"))
    return await OrderService.dispatch_order(db, tenant_id, order_id, x_idempotency_key)

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: uuid.UUID,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_tenant_db_session)
):
    """Obtiene el detalle de un pedido por su ID."""
    tenant_id = uuid.UUID(decode_token(token).get("tenant_id"))
    return await OrderService.get_order_by_id(db, tenant_id, order_id)