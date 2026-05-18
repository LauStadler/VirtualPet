# Virtual Pet — API

Ecommerce 100% digital de productos para mascotas. Cobertura: Mar del Plata.

## Stack
- **Backend**: Python 3.12 + FastAPI
- **Base de datos**: MySQL (AWS RDS)
- **ORM**: SQLAlchemy + Alembic
- **Imágenes**: AWS S3 + CloudFront
- **Pagos**: Simulado (botón)
- **Deploy**: AWS Elastic Beanstalk — región São Paulo

## Estructura

```
virtual-pet/
├── main.py                        # Punto de entrada, registro de routers
├── requirements.txt
├── Procfile                       # Comando de inicio para AWS EB
├── alembic.ini
├── .env.example
│
├── modules/                       # Módulos de negocio
│   ├── auth/                      # Login, registro, roles
│   ├── catalog/                   # Productos, categorías, stock
│   ├── sales/                     # Carrito y checkout
│   ├── payments/                  # Pago simulado
│   └── orders/                    # Pedidos, envíos, trazabilidad
│
├── backoffice/                    # Vistas para equipo de depósito
│
├── shared/                        # Código compartido
│   ├── config/settings.py
│   ├── dependencies/
│   │   ├── database.py            # Sesión MySQL vía SQLAlchemy
│   │   └── auth.py                # get_current_user, require_role()
│   ├── exceptions/handlers.py
│   ├── middleware/
│   └── utils/
│       └── security.py            # Hash bcrypt + JWT
│
├── infrastructure/
│   ├── db/base.py                 # Base declarativa SQLAlchemy
│   ├── storage/s3_service.py      # AWS S3
│   └── courier/courier_service.py
│
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

## Levantar en local

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # completar DATABASE_URL y SECRET_KEY
alembic upgrade head
uvicorn main:app --reload
# Docs: http://localhost:8000/docs
```
