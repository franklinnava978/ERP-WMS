import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.middleware.tenant import get_tenant_db_session, oauth2_scheme
from src.core.security import decode_token
from src.modules.integrations.schemas import WebhookCreate, WebhookResponse, EventResponse
from src.modules.integrations.service import IntegrationService

router = APIRouter(prefix="/integrations", tags=["Integraciones & Webhooks"])

@router.post("/webhooks", response_model=WebhookResponse, status_code=status.HTTP_201_CREATED)
async def register_webhook(
    payload: WebhookCreate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_tenant_db_session)
):
    """Registra una nueva URL para recibir eventos del WMS."""
    tenant_id = uuid.UUID(decode_token(token).get("tenant_id"))
    return await IntegrationService.create_webhook(db, tenant_id, payload)

@router.get("/webhooks", response_model=list[WebhookResponse])
async def list_webhooks(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_tenant_db_session)
):
    """Lista las suscripciones de webhooks del Tenant."""
    tenant_id = uuid.UUID(decode_token(token).get("tenant_id"))
    return await IntegrationService.list_webhooks(db, tenant_id)

@router.get("/events", response_model=list[EventResponse])
async def get_integration_events(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_tenant_db_session)
):
    """Obtiene los últimos eventos de integración y su estado (Logs)."""
    tenant_id = uuid.UUID(decode_token(token).get("tenant_id"))
    return await IntegrationService.get_recent_events(db, tenant_id)