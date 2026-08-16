import uuid
from fastapi import HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.catalog.models import UnitOfMeasure, Product, UOMConversion
from src.modules.catalog.schemas import UOMCreate, ProductCreate, UOMConversionCreate

class CatalogService:

    # --- UOM ---
    @staticmethod
    async def create_uom(db: AsyncSession, tenant_id: uuid.UUID, dto: UOMCreate) -> UnitOfMeasure:
        code_clean = dto.code.strip().upper()
        query = select(UnitOfMeasure).where(
            UnitOfMeasure.tenant_id == tenant_id,
            UnitOfMeasure.code == code_clean
        )
        res = await db.execute(query)
        if res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La UOM '{code_clean}' ya existe en este tenant."
            )

        uom = UnitOfMeasure(
            tenant_id=tenant_id,
            code=code_clean,
            name=dto.name.strip()
        )
        db.add(uom)
        await db.commit()
        await db.refresh(uom)
        return uom

    @staticmethod
    async def list_uoms(db: AsyncSession, tenant_id: uuid.UUID) -> list[UnitOfMeasure]:
        query = select(UnitOfMeasure).where(UnitOfMeasure.tenant_id == tenant_id)
        res = await db.execute(query)
        return list(res.scalars().all())

    # --- PRODUCTOS ---
    @staticmethod
    async def create_product(db: AsyncSession, tenant_id: uuid.UUID, dto: ProductCreate) -> Product:
        sku_clean = dto.sku.strip().upper()
        
        # Validar duplicados
        query = select(Product).where(Product.tenant_id == tenant_id, Product.sku == sku_clean)
        res = await db.execute(query)
        if res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El SKU '{sku_clean}' ya existe."
            )

        # Validar UOMs existentes
        inv_uom = await db.get(UnitOfMeasure, dto.inventory_uom_id)
        val_uom = await db.get(UnitOfMeasure, dto.valuation_uom_id)
        if not inv_uom or inv_uom.tenant_id != tenant_id or not val_uom or val_uom.tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las UOMs especificadas no son válidas para este tenant."
            )

        product = Product(
            tenant_id=tenant_id,
            sku=sku_clean,
            name=dto.name.strip(),
            inventory_uom_id=dto.inventory_uom_id,
            valuation_uom_id=dto.valuation_uom_id
        )
        db.add(product)
        await db.commit()
        await db.refresh(product)
        return product

    @staticmethod
    async def list_products(db: AsyncSession, tenant_id: uuid.UUID) -> list[Product]:
        query = select(Product).where(Product.tenant_id == tenant_id, Product.is_active == True)
        res = await db.execute(query)
        return list(res.scalars().all())

    # --- CONVERSIONES UOM ---
    @staticmethod
    async def create_conversion(db: AsyncSession, tenant_id: uuid.UUID, dto: UOMConversionCreate) -> UOMConversion:
        product = await db.get(Product, dto.product_id)
        if not product or product.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado.")

        conversion = UOMConversion(
            tenant_id=tenant_id,
            product_id=dto.product_id,
            from_uom_id=dto.from_uom_id,
            to_uom_id=dto.to_uom_id,
            conversion_factor=dto.conversion_factor
        )
        db.add(conversion)
        await db.commit()
        await db.refresh(conversion)
        return conversion