import uuid
from fastapi import HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.tenants.models import Tenant
from src.modules.tenants.schemas import TenantCreate

class TenantService:

    @staticmethod
    async def create_tenant(db: AsyncSession, dto: TenantCreate) -> Tenant:
        clean_code = dto.code.strip().upper()
        
        # Validar duplicados de código
        query = select(Tenant).where(Tenant.code == clean_code)
        result = await db.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El código de tenant '{clean_code}' ya existe."
            )
        
        new_tenant = Tenant(
            code=clean_code,
            name=dto.name.strip()
        )
        db.add(new_tenant)
        await db.commit()
        await db.refresh(new_tenant)
        return new_tenant

    @staticmethod
    async def get_by_id(db: AsyncSession, tenant_id: uuid.UUID) -> Tenant:
        tenant = await db.get(Tenant, tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant no encontrado."
            )
        return tenant

    @staticmethod
    async def list_all(db: AsyncSession) -> list[Tenant]:
        query = select(Tenant).order_by(Tenant.created_at.desc())
        result = await db.execute(query)
        return list(result.scalars().all())