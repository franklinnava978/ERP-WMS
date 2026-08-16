import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.middleware.tenant import get_tenant_db_session, oauth2_scheme
from src.core.security import decode_token
from src.modules.catalog.schemas import (
    UOMCreate, UOMResponse, ProductCreate, ProductResponse, UOMConversionCreate, UOMConversionResponse
)
from src.modules.catalog.service import CatalogService

router = APIRouter(prefix="/catalog", tags=["Catálogo Maestro (UOM & Productos)"])

# Unidades de Medida
@router.post("/uom", response_model=UOMResponse, status_code=status.HTTP_201_CREATED)
async def create_uom(
    payload: UOMCreate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_tenant_db_session)
):
    tenant_id = uuid.UUID(decode_token(token).get("tenant_id"))
    return await CatalogService.create_uom(db, tenant_id, payload)

@router.get("/uom", response_model=list[UOMResponse])
async def list_uoms(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_tenant_db_session)
):
    tenant_id = uuid.UUID(decode_token(token).get("tenant_id"))
    return await CatalogService.list_uoms(db, tenant_id)

# Productos
@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_tenant_db_session)
):
    tenant_id = uuid.UUID(decode_token(token).get("tenant_id"))
    return await CatalogService.create_product(db, tenant_id, payload)

@router.get("/products", response_model=list[ProductResponse])
async def list_products(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_tenant_db_session)
):
    tenant_id = uuid.UUID(decode_token(token).get("tenant_id"))
    return await CatalogService.list_products(db, tenant_id)

# Conversiones
@router.post("/conversions", response_model=UOMConversionResponse, status_code=status.HTTP_201_CREATED)
async def create_conversion(
    payload: UOMConversionCreate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_tenant_db_session)
):
    tenant_id = uuid.UUID(decode_token(token).get("tenant_id"))
    return await CatalogService.create_conversion(db, tenant_id, payload)