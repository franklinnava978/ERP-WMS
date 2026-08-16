import uuid
from fastapi import HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.topology.models import Location, LocationType
from src.modules.topology.schemas import LocationCreate, LocationStockToggle

class TopologyService:

    @staticmethod
    async def create_location(db: AsyncSession, tenant_id: uuid.UUID, dto: LocationCreate) -> Location:
        code_clean = dto.code.strip().upper()

        # Validar duplicados por tenant
        query = select(Location).where(Location.tenant_id == tenant_id, Location.code == code_clean)
        res = await db.execute(query)
        if res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La ubicación con código '{code_clean}' ya existe."
            )

        # Validar ubicación padre si aplica
        if dto.parent_id:
            parent = await db.get(Location, dto.parent_id)
            if not parent or parent.tenant_id != tenant_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La ubicación padre especificada no existe o no pertenece al tenant."
                )

        location = Location(
            tenant_id=tenant_id,
            parent_id=dto.parent_id,
            code=code_clean,
            name=dto.name.strip(),
            location_type=dto.location_type,
            stock_enabled=dto.stock_enabled
        )
        db.add(location)
        await db.commit()
        await db.refresh(location)
        return location

    @staticmethod
    async def list_locations(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        location_type: Optional[LocationType] = None
    ) -> list[Location]:
        query = select(Location).where(Location.tenant_id == tenant_id)
        if location_type:
            query = query.where(Location.location_type == location_type)
        res = await db.execute(query)
        return list(res.scalars().all())

    @staticmethod
    async def toggle_stock(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        location_id: uuid.UUID,
        dto: LocationStockToggle
    ) -> Location:
        location = await db.get(Location, location_id)
        if not location or location.tenant_id != tenant_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ubicación no encontrada.")

        location.stock_enabled = dto.stock_enabled
        db.add(location)
        await db.commit()
        await db.refresh(location)
        return location