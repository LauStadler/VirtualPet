"""
Controller del módulo sales.

Expone el único endpoint de ventas: el checkout.
Al usar carrito en el frontend, no hay endpoints para agregar,
quitar o listar items del carrito — esa responsabilidad es del frontend.

Endpoint:
    POST /cart/checkout  → procesa el carrito y crea una orden
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from shared.dependencies.database import get_db
from shared.dependencies.auth import get_current_user
from modules.sales.services.sales_service import SalesService, ProductoInvalidoError
from modules.catalog.services.catalog_service import StockInsuficienteError
from modules.sales.schemas.sales_schema import CheckoutRequest, CheckoutResponse
from modules.auth.models.user import User

router = APIRouter()


@router.post(
    "/checkout",
    response_model=CheckoutResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Confirmar compra",
    description=(
        "Procesa el carrito del cliente y crea una orden de compra. "
        "Verifica stock y calcula el total con precios actualizados desde la DB. "
        "El pago se considera aprobado automáticamente (simulado). "
        "Requiere autenticación — solo clientes pueden comprar."
    ),
)
def checkout(
    body: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CheckoutResponse:
    """
    Requiere: JWT válido de un usuario con rol cliente.

    El frontend envía el estado completo del carrito.
    La API recalcula precios desde la DB para evitar manipulación
    de precios desde el cliente.

    Posibles errores:
    - 404: Algún producto no existe o fue desactivado por el ERP.
    - 422: Algún producto no tiene stock suficiente.
    """
    service = SalesService(db)

    try:
        return service.checkout(datos=body, user_id=current_user.id)

    except ProductoInvalidoError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except StockInsuficienteError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Sin stock suficiente para el producto {e.product_id}. "
                f"Disponible: {e.disponible}, solicitado: {e.solicitado}."
            )
        )
