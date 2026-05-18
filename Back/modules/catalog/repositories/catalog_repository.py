"""
Repositorio del catálogo de productos.

Centraliza todas las queries a las tablas 'products', 'categories' y 'stock'.
Al ser un módulo de solo lectura desde la API, todas las operaciones aquí
son SELECT — el ERP escribe directamente en MySQL.

La única excepción es descontar_stock(), que es llamada internamente
por el módulo de orders al confirmar una compra, nunca por un endpoint HTTP.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, or_
from typing import Optional

from modules.catalog.models.product import Product
from modules.catalog.models.category import Category
from modules.catalog.models.stock import Stock


class CatalogRepository:
    """Acceso a datos para productos, categorías y stock."""

    def __init__(self, db: Session) -> None:
        """
        Args:
            db: Sesión activa de SQLAlchemy inyectada por FastAPI.
        """
        self.db = db

    # ── Productos ──────────────────────────────────────────────────────────────

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """
        Busca un producto por ID incluyendo su categoría y stock en una sola query.
        Usa joinedload para evitar el problema N+1 al acceder a las relaciones.

        Args:
            product_id: ID del producto a buscar.

        Returns:
            El producto con category y stock cargados, o None si no existe.
        """
        stmt = (
            select(Product)
            .options(
                joinedload(Product.category),
                joinedload(Product.stock),
            )
            .where(Product.id == product_id, Product.activo == True)
        )
        return self.db.scalar(stmt)

    def list_products(
        self,
        busqueda: Optional[str] = None,
        categoria_id: Optional[int] = None,
        solo_con_stock: bool = True,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Product], int]:
        """
        Lista productos activos con filtros opcionales y paginación.

        La búsqueda por texto opera sobre nombre y descripción con LIKE.
        Para un catálogo con muchos productos se podría migrar a full-text search,
        pero LIKE es suficiente para el volumen esperado de Virtual Pet.

        Args:
            busqueda: Texto libre para buscar en nombre y descripción.
            categoria_id: Filtra por categoría. Incluye productos de subcategorías
                          (hijos de la categoría dada).
            solo_con_stock: Si True, excluye productos con stock = 0.
            page: Página actual (base 1).
            page_size: Cantidad de resultados por página.

        Returns:
            Tupla con (lista de productos, total de resultados sin paginar).
        """
        stmt = (
            select(Product)
            .options(joinedload(Product.stock))
            .where(Product.activo == True)
        )

        # Filtro de búsqueda por texto
        if busqueda:
            termino = f"%{busqueda}%"
            stmt = stmt.where(
                or_(
                    Product.nombre.ilike(termino),
                    Product.descripcion.ilike(termino),
                )
            )

        # Filtro por categoría: incluye la categoría dada y sus hijos directos
        if categoria_id:
            subcategory_ids_stmt = select(Category.id).where(
                Category.parent_id == categoria_id
            )
            subcategory_ids = [row[0] for row in self.db.execute(subcategory_ids_stmt)]
            all_category_ids = [categoria_id] + subcategory_ids
            stmt = stmt.where(Product.category_id.in_(all_category_ids))

        # Filtro de stock: excluye productos agotados si se solicita
        if solo_con_stock:
            stmt = stmt.join(Product.stock).where(Stock.cantidad > 0)

        # Conteo total antes de paginar (para metadatos de paginación)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.scalar(count_stmt)

        # Paginación
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        products = list(self.db.scalars(stmt).unique())
        return products, total

    # ── Categorías ────────────────────────────────────────────────────────────

    def list_categories(self) -> list[Category]:
        """
        Retorna todas las categorías ordenadas por nombre.
        Usado para poblar el filtro de categorías en el frontend.

        Returns:
            Lista de todas las categorías disponibles.
        """
        stmt = select(Category).order_by(Category.nombre)
        return list(self.db.scalars(stmt))

    # ── Stock ─────────────────────────────────────────────────────────────────

    def get_stock(self, product_id: int) -> Optional[Stock]:
        """
        Obtiene el registro de stock de un producto específico.

        Args:
            product_id: ID del producto a consultar.

        Returns:
            El objeto Stock, o None si el producto no tiene registro de stock.
        """
        stmt = select(Stock).where(Stock.product_id == product_id)
        return self.db.scalar(stmt)

    def hay_stock_suficiente(self, product_id: int, cantidad: int) -> bool:
        """
        Verifica si hay suficiente stock para satisfacer una cantidad pedida.

        Llamado por el módulo de sales en el momento del checkout,
        antes de procesar el pago simulado.

        Args:
            product_id: ID del producto a verificar.
            cantidad: Unidades que se quieren comprar.

        Returns:
            True si hay stock suficiente, False si no alcanza o no hay registro.
        """
        stock = self.get_stock(product_id)
        if stock is None:
            return False
        return stock.cantidad >= cantidad

    def descontar_stock(self, product_id: int, cantidad: int) -> Stock:
        """
        Descuenta unidades del stock al confirmar una compra.

        IMPORTANTE: Este método debe llamarse únicamente después de verificar
        que hay stock suficiente con hay_stock_suficiente(). No hace
        validación propia para evitar doble consulta en el flujo de checkout.

        Este método es llamado por orders/services/order_service.py
        al confirmar una compra. Nunca es llamado directamente por un endpoint.

        Args:
            product_id: ID del producto a descontar.
            cantidad: Unidades a restar del stock.

        Returns:
            El objeto Stock actualizado con la nueva cantidad.

        Raises:
            ValueError: Si no existe registro de stock para el producto.
        """
        stock = self.get_stock(product_id)
        if stock is None:
            raise ValueError(
                f"No existe registro de stock para el producto {product_id}. "
                "El ERP debe inicializar el stock antes de que el producto pueda venderse."
            )

        stock.cantidad -= cantidad
        self.db.commit()
        self.db.refresh(stock)
        return stock
