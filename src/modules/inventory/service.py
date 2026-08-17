from datetime import datetime, timezone
from typing import Optional
import uuid
from fastapi import HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.inventory.models import Stock, InventoryLog, MovementType
from src.modules.inventory.schemas import StockMoveRequest, StockReserveRequest
from src.modules.topology.models import Location

class InventoryService:

    @staticmethod
    async def _check_idempotency(db: AsyncSession, key: str) -> Optional[InventoryLog]:
        query = select(InventoryLog).where(InventoryLog.idempotency_key == key)
        res = await db.execute(query)
        return res.scalar_one_or_none()

    @staticmethod
    async def move_stock(db: AsyncSession, tenant_id: uuid.UUID, dto: StockMoveRequest) -> InventoryLog:
        # 1. Control de Idempotencia para PDAs Zebra
        existing_log = await InventoryService._check_idempotency(db, dto.idempotency_key)
        if existing_log:
            return existing_log

        # 2. Validar que la ubicación de destino acepte stock si está definida
        if dto.destination_location_id:
            dest_loc = await db.get(Location, dto.destination_location_id)
            if not dest_loc or dest_loc.tenant_id != tenant_id:
                raise HTTPException(status_code=400, detail="Ubicación de destino no válida.")
            if not dest_loc.stock_enabled:
                raise HTTPException(status_code=400, detail="La ubicación de destino no permite almacenamiento de stock.")

        # 3. Descontar de Origen
        if dto.origin_location_id:
            orig_q = select(Stock).where(
                Stock.tenant_id == tenant_id,
                Stock.location_id == dto.origin_location_id,
                Stock.product_id == dto.product_id,
                Stock.lpn_code == dto.lpn_code
            )
            orig_res = await db.execute(orig_q)
            orig_stock = orig_res.scalar_one_or_none()

            if not orig_stock or orig_stock.quantity_available < dto.quantity:
                raise HTTPException(status_code=400, detail="Stock insuficiente en origen.")

            orig_stock.quantity_available -= dto.quantity
            orig_stock.updated_at = datetime.now(timezone.utc)
            db.add(orig_stock)

        # 4. Acreditar en Destino
        if dto.destination_location_id:
            dest_q = select(Stock).where(
                Stock.tenant_id == tenant_id,
                Stock.location_id == dto.destination_location_id,
                Stock.product_id == dto.product_id,
                Stock.lpn_code == dto.lpn_code
            )
            dest_res = await db.execute(dest_q)
            dest_stock = dest_res.scalar_one_or_none()

            if not dest_stock:
                dest_stock = Stock(
                    tenant_id=tenant_id,
                    location_id=dto.destination_location_id,
                    product_id=dto.product_id,
                    lpn_code=dto.lpn_code,
                    quantity_available=dto.quantity
                )
            else:
                dest_stock.quantity_available += dto.quantity
                dest_stock.updated_at = datetime.now(timezone.utc)
            db.add(dest_stock)

        # 5. Registro Audit Log
        m_type = MovementType.TRANSFER if (dto.origin_location_id and dto.destination_location_id) else (
            MovementType.INBOUND if dto.destination_location_id else MovementType.OUTBOUND
        )

        log = InventoryLog(
            tenant_id=tenant_id,
            product_id=dto.product_id,
            origin_location_id=dto.origin_location_id,
            destination_location_id=dto.destination_location_id,
            lpn_code=dto.lpn_code,
            movement_type=m_type,
            quantity=dto.quantity,
            idempotency_key=dto.idempotency_key
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log

    @staticmethod
    async def get_stock_by_location(db: AsyncSession, tenant_id: uuid.UUID, location_id: uuid.UUID) -> list[Stock]:
        query = select(Stock).where(Stock.tenant_id == tenant_id, Stock.location_id == location_id)
        res = await db.execute(query)
        return list(res.scalars().all())