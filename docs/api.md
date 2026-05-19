# Documentacion de la API - Virtual Pet

Esta es la documentacion de referencia para la API de Virtual Pet. La API esta construida con **FastAPI** y sigue los principios REST.

## Informacion General

- **Formato de datos:** JSON
- **Codificacion:** UTF-8
- **Autenticacion:** JWT (JSON Web Token)

---

## Autenticacion

Para los endpoints protegidos, se requiere un token en el header `Authorization`.

**Formato:**
`Authorization: Bearer <TU_TOKEN_AQUI>`

### Endpoints de Auth
- `POST /auth/register`: Registro de nuevos clientes.
- `POST /auth/login`: Inicio de sesion (devuelve el token).
- `GET /auth/me`: Ver perfil del usuario conectado.

---

## Catalogo

Endpoints publicos para explorar productos.

### `GET /catalog/products`
Lista de productos con soporte para filtros y paginacion.

**Parametros de busqueda (Query):**
- `busqueda`: (string) Filtra por nombre o descripcion.
- `categoria_id`: (int) Filtra por una categoria especifica.
- `solo_con_stock`: (bool, default: true) Oculta productos agotados.
- `page`: (int, default: 1) Numero de pagina.

---

## Ventas y Pedidos

### `POST /cart/checkout` (Requiere Auth)
Crea una orden de compra a partir de los items del carrito.

**Cuerpo del pedido (JSON):**
```json
{
  "items": [
    { "product_id": 1, "cantidad": 2 }
  ],
  "direccion_entrega": "Av. Colon 1234, Mar del Plata"
}
```

### `GET /orders` (Requiere Auth)
Lista el historial de pedidos del cliente.

---

## Backoffice (Solo Personal)

Endpoints protegidos para roles `ADMIN` o `DEPOSITO`.

- `GET /backoffice/orders`: Ver todos los pedidos de la plataforma.
- `PATCH /backoffice/orders/{id}/estado`: Avanzar el estado de un pedido.
  - Flujo: `pendiente` -> `en_preparacion` -> `despachado` -> `en_camino` -> `entregado`.
