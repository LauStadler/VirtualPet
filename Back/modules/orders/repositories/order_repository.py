"""
Repositorio de órdenes.

Centraliza todas las queries a las tablas 'orders' y 'order_items'.
Incluye operaciones tanto para el cliente (sus propias órdenes)
como para el backoffice (todas las órdenes).
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
from typing import Optional

from modules.orders.models.order import Order, OrderEstado
from modules.orders.models.order_item import OrderItem
from modules.sales.schemas.sales_schema import CheckoutItemDetail


class OrderRepository:
    """Acceso a datos para las entidades Order y OrderItem."""

    def __init__(self, db: Session) -> None:
        """
        Args:
            db: Sesión activa de SQLAlchemy inyectada por FastAPI.
        """
        self.db = db

    def crear(
        self,
        user_id: int,
        items: list[CheckoutItemDetail],
        total: float,
        direccion_entrega: str,
    ) -> Order:
        """
        Crea una nueva orden con sus items en una sola transacción.

        Los items se persisten como snapshot de la compra: precio_unitario
        y subtotal se guardan tal como fueron calculados al momento del checkout,
        independientemente de cambios futuros en el catálogo.

        Args:
            user_id: ID del usuario que realiza la compra.
            items: Items validados por SalesService con precios confirmados.
            total: Total calculado por SalesService.
            direccion_entrega: Dirección ingresada por el cliente.

        Returns:
            La orden recién creada con sus items cargados.
        """
        order = Order(
            user_id=user_id,
            total=total,
            direccion_entrega=direccion_entrega,
            estado=OrderEstado.PENDIENTE,
        )
        self.db.add(order)
        self.db.flush()  # genera order.id sin hacer commit aún

        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                cantidad=item.cantidad,
                precio_unitario=item.precio_unitario,
                producto_nombre=item.producto_nombre,
                subtotal=item.subtotal,
            )
            self.db.add(order_item)

        self.db.commit()
        self.db.refresh(order)
        return order

    def get_by_id(self, order_id: int) -> Optional[Order]:
        """
        Busca una orden por ID incluyendo sus items en una sola query.

        Args:
            order_id: ID de la orden a buscar.

        Returns:
            La orden con items cargados, o None si no existe.
        """
        stmt = (
            select(Order)
            .options(joinedload(Order.items))
            .where(Order.id == order_id)
        )
        return self.db.scalar(stmt)

    def get_by_id_and_user(self, order_id: int, user_id: int) -> Optional[Order]:
        """
        Busca una orden por ID verificando que pertenezca al usuario dado.
        Usado por el endpoint del cliente para evitar que vea órdenes ajenas.

        Args:
            order_id: ID de la orden a buscar.
            user_id: ID del usuario que hace la consulta.

        Returns:
            La orden si existe y pertenece al usuario, None en caso contrario.
        """
        stmt = (
            select(Order)
            .options(joinedload(Order.items))
            .where(Order.id == order_id, Order.user_id == user_id)
        )
        return self.db.scalar(stmt)

    def list_by_user(self, user_id: int) -> list[Order]:
        """
        Lista todas las órdenes de un usuario ordenadas por fecha descendente.
        Usado por el cliente para ver su historial de compras.

        Args:
            user_id: ID del usuario a consultar.

        Returns:
            Lista de órdenes del usuario, la más reciente primero.
        """
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        return list(self.db.scalars(stmt))

    def list_all(self) -> list[Order]:
        """
        Lista todas las órdenes del sistema ordenadas por fecha descendente.
        Usado exclusivamente por el backoffice — nunca por endpoints del cliente.

        Returns:
            Lista de todas las órdenes, la más reciente primero.
        """
        stmt = (
            select(Order)
            .options(joinedload(Order.items), joinedload(Order.user))
            .order_by(Order.created_at.desc())
        )
        return list(self.db.scalars(stmt).unique())

    def actualizar_estado(self, order: Order, nuevo_estado: OrderEstado) -> Order:
        """
        Actualiza el estado de una orden.
        La validación de que la transición es válida se hace en OrderService,
        no aquí — el repositorio solo persiste el cambio.

        Args:
            order: Objeto Order a actualizar.
            nuevo_estado: Nuevo estado a asignar.

        Returns:
            La orden actualizada.
        """
        order.estado = nuevo_estado
        self.db.commit()
        self.db.refresh(order)
        return order
