# Virtual Pet — Plataforma E-commerce

Plataforma integral para la venta de productos de mascotas con cobertura en Mar del Plata. El ecosistema se compone de una API robusta, una tienda para clientes y un panel de gestión para logística.

## Arquitectura del Sistema

El proyecto está organizado en tres componentes principales:

1.  **Backend (API)**: Núcleo de negocio, gestión de stock y procesamiento de órdenes.
2.  **Frontend Cliente**: Tienda virtual responsiva para los usuarios finales.
3.  **Frontend Depósito**: Panel de control para la gestión de pedidos y logística.

## Stack Tecnológico

### Backend
- **Lenguaje**: Python 3.12
- **Framework**: FastAPI
- **Base de Datos**: MySQL (AWS RDS)
- **ORM**: SQLAlchemy + Alembic (Migraciones)
- **Almacenamiento**: AWS S3 + CloudFront (Imágenes de productos)
- **Infraestructura**: AWS Elastic Beanstalk

### Frontend (Cliente & Depósito)
- **Framework**: React (v18/v19) + Vite
- **Estilos**: Tailwind CSS
- **Estado**: Zustand (Gestión global de carrito y auth)
- **Comunicación**: Axios
- **Iconos**: Lucide React
- **Logística**: @hello-pangea/dnd (Tablero Kanban en Depósito)

## Estructura del Repositorio

```
VirtualPet/
├── Back/                      # Código del Servidor
│   ├── modules/               # Módulos de negocio (Auth, Catalog, Orders, Sales, Payments)
│   ├── shared/                # Lógica compartida, config y seguridad
│   ├── infrastructure/        # Adaptadores de DB y S3
│   ├── backoffice/            # Controladores específicos de administración
│   └── main.py                # Punto de entrada de la API
│
├── Front/                     # Tienda Virtual (Cliente)
│   ├── src/components/        # UI reusable (Carrito, Productos)
│   ├── src/store/             # Estados de Zustand
│   └── src/pages/             # Vistas principales del e-commerce
│
├── FrontDeposito/             # Panel de Logística (Backoffice)
│   ├── src/components/Board/  # Tablero Kanban de seguimiento
│   └── src/pages/             # Gestión de órdenes y estados
│
└── docs/                      # Documentación y diagramas
```

## Configuración del Entorno

### Backend
```bash
cd Back
python -m venv venv
# Windows: venv\Scripts\activate | Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # Configurar DATABASE_URL y AWS_KEYS
alembic upgrade head
uvicorn main:app --reload
```
*API Docs: http://localhost:8000/docs*

### Frontend (Tienda & Depósito)
```bash
# Para ambos directorios (Front y FrontDeposito)
npm install
npm run dev
```
*Tienda: http://localhost:5173 | Depósito: http://localhost:5174*

## Notas de Desarrollo
- El sistema utiliza **JWT** para autenticación persistente.
- La gestión de stock es **atómica** durante el proceso de checkout.
- Las imágenes son servidas a través de una red de contenido (CDN) para optimizar el rendimiento.
