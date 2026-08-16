import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db_session
from src.modules.tenants.schemas import TenantCreate, TenantResponse
from src.modules.tenants.service import TenantService

router = APIRouter(prefix="/tenants", tags=["Tenants"])

@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    payload: TenantCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Crea y aprovisiona un nuevo Tenant en la plataforma."""
    return await TenantService.create_tenant(db, payload)

@router.get("", response_model=list[TenantResponse])
async def list_tenants(db: AsyncSession = Depends(get_db_session)):
    """Lista todos los tenants registrados."""
    return await TenantService.list_all(db)

@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Obtiene el detalle de un Tenant específico."""
    return await TenantService.get_by_id(db, tenant_id)