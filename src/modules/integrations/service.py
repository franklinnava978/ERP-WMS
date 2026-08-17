import uuid
from fastapi import HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.integrations.models import WebhookSubscription, IntegrationEvent, EventType, IntegrationStatus
from src.modules.integrations.schemas import WebhookCreate

class IntegrationService:

    @staticmethod
    async def create_webhook(db: AsyncSession, tenant_id: uuid.UUID, dto: WebhookCreate) -> WebhookSubscription:
        # Validar si ya existe una suscripción para este evento y URL
        query = select(WebhookSubscription).where(
            WebhookSubscription.tenant_id == tenant_id,
            WebhookSubscription.event_type == dto.event_type,
            WebhookSubscription.target_url == str(dto.target_url)
        )
        res = await db.execute(query)
        if res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una suscripción para este evento y URL."
            )

        webhook = WebhookSubscription(
            tenant_id=tenant_id,
            target_url=str(dto.target_url),
            secret_key=dto.secret_key,
            event_type=dto.event_type
        )
        db.add(webhook)
        await db.commit()
        await db.refresh(webhook)
        return webhook

    @staticmethod
    async def list_webhooks(db: AsyncSession, tenant_id: uuid.UUID) -> list[WebhookSubscription]:
        query = select(WebhookSubscription).where(WebhookSubscription.tenant_id == tenant_id)
        res = await db.execute(query)
        return list(res.scalars().all())

    @staticmethod
    async def log_event(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        event_type: EventType,
        payload: dict
    ) -> IntegrationEvent:
        """Registra un evento para ser procesado y enviado a los webhooks activos (Background Task futura)."""
        event = IntegrationEvent(
            tenant_id=tenant_id,
            event_type=event_type,
            payload=payload,
            status=IntegrationStatus.PENDING
        )
        db.add(event)
        await db.commit()
        await db.refresh(event)
        return event

    @staticmethod
    async def get_recent_events(db: AsyncSession, tenant_id: uuid.UUID, limit: int = 50) -> list[IntegrationEvent]:
        query = select(IntegrationEvent).where(
            IntegrationEvent.tenant_id == tenant_id
        ).order_by(IntegrationEvent.created_at.desc()).limit(limit)
        res = await db.execute(query)
        return list(res.scalars().all())