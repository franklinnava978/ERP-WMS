from datetime import datetime, timezone
import uuid
from fastapi import HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.modules.orders.models import Order, OrderItem, OrderStatus
from src.modules.orders.schemas import OrderCreate
from src.modules.inventory.models import Stock, InventoryLog, MovementType

class OrderService:

    @staticmethod
    async def create_order(db: AsyncSession, tenant_id: uuid.UUID, dto: OrderCreate) -> Order:
        clean_number = dto.order_number.strip().upper()

        # Validar número de pedido único
        query = select(Order).where(Order.tenant_id == tenant_id, Order.order_number == clean_number)
        res = await db.execute(query)
        if res.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"El pedido '{clean_number}' ya existe."
            )

        new_order = Order(
            tenant_id=tenant_id,
            order_number=clean_number,
            customer_name=dto.customer_name.strip(),
            location_id=dto.location_id,
            status=OrderStatus.DRAFT
        )
        db.add(new_order)
        await db.commit()
        await db.refresh(new_order)

        for item_dto in dto.items:
            item = OrderItem(
                tenant_id=tenant_id,
                order_id=new_order.id,
                product_id=item_dto.product_id,
                quantity_requested=item_dto.quantity_requested,
                quantity_reserved=0.0
            )
            db.add(item)

        await db.commit()
        return await OrderService.get_order_by_id(db, tenant_id, new_order.id)

    @staticmethod
    async def get_order_by_id(db: AsyncSession, tenant_id: uuid.UUID, order_id: uuid.UUID) -> Order:
        query = (
            select(Order)
            .where(Order.tenant_id == tenant_id, Order.id == order_id)
            .options(selectinload(Order.items))
        )
        res = await db.execute(query)
        order = res.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado.")
        return order

    @staticmethod
    async def reserve_stock_for_order(db: AsyncSession, tenant_id: uuid.UUID, order_id: uuid.UUID) -> Order:
        order = await OrderService.get_order_by_id(db, tenant_id, order_id)
        if order.status != OrderStatus.DRAFT:
            raise HTTPException(status_code=400, detail="Solo se pueden reservar pedidos en estado DRAFT.")

        for item in order.items:
            # Buscar stock disponible en la bodega del pedido
            stock_q = select(Stock).where(
                Stock.tenant_id == tenant_id,
                Stock.location_id == order.location_id,
                Stock.product_id == item.product_id
            )
            stock_res = await db.execute(stock_q)
            stock_list = list(stock_res.scalars().all())

            total_available = sum(s.quantity_available for s in stock_list)
            if total_available < item.quantity_requested:
                raise HTTPException(
                    status_code=400,
                    detail=f"Stock insuficiente para el producto {item.product_id}. Requerido: {item.quantity_requested}, Disponible: {total_available}"
                )

            needed = item.quantity_requested
            for s in stock_list:
                if needed <= 0:
                    break
                take = min(s.quantity_available, needed)
                s.quantity_available -= take
                s.quantity_reserved += take
                s.updated_at = datetime.now(timezone.utc)
                needed -= take
                db.add(s)

            item.quantity_reserved = item.quantity_requested
            db.add(item)

        order.status = OrderStatus.RESERVED
        db.add(order)
        await db.commit()
        return await OrderService.get_order_by_id(db, tenant_id, order_id)

    @staticmethod
    async def dispatch_order(
        db: AsyncSession,
        tenant_id: uuid.UUID,
        order_id: uuid.UUID,
        idempotency_key: str
    ) -> Order:
        order = await OrderService.get_order_by_id(db, tenant_id, order_id)
        if order.status not in [OrderStatus.RESERVED, OrderStatus.PICKED]:
            raise HTTPException(status_code=400, detail="El pedido debe estar reservado o recolectado para despacharse.")

        for item in order.items:
            stock_q = select(Stock).where(
                Stock.tenant_id == tenant_id,
                Stock.location_id == order.location_id,
                Stock.product_id == item.product_id
            )
            stock_res = await db.execute(stock_q)
            stock_list = list(stock_res.scalars().all())

            remaining_to_release = item.quantity_reserved
            for s in stock_list:
                if remaining_to_release <= 0:
                    break
                release = min(s.quantity_reserved, remaining_to_release)
                s.quantity_reserved -= release
                s.updated_at = datetime.now(timezone.utc)
                remaining_to_release -= release
                db.add(s)

            # Registrar log de salida definitiva
            log = InventoryLog(
                tenant_id=tenant_id,
                product_id=item.product_id,
                origin_location_id=order.location_id,
                destination_location_id=None,
                movement_type=MovementType.OUTBOUND,
                quantity=item.quantity_reserved,
                idempotency_key=f"{idempotency_key}_{item.id}"
            )
            db.add(log)

        order.status = OrderStatus.DISPATCHED
        db.add(order)
        await db.commit()
        return await OrderService.get_order_by_id(db, tenant_id, order_id)