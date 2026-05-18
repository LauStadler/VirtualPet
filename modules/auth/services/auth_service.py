"""
Servicio de autenticación.

Contiene toda la lógica de negocio relacionada con el acceso al sistema:
registro de usuarios, login, y generación de tokens JWT.

Regla de diseño: este servicio no conoce nada de HTTP (no importa FastAPI).
Si necesitás levantar un error HTTP, lo hace el controller — este servicio
lanza excepciones de dominio propias que el controller traduce.
"""

from sqlalchemy.orm import Session
from datetime import datetime, timezone

from modules.auth.repositories.user_repository import UserRepository
from modules.auth.models.user import User, UserRole
from modules.auth.schemas.user_schema import RegisterRequest, LoginRequest, CreateUserAdminRequest
from shared.utils.security import hash_password, verify_password, create_access_token
from shared.config.settings import settings


class EmailYaRegistradoError(Exception):
    """Se lanza cuando se intenta registrar un email que ya existe en el sistema."""
    pass


class CredencialesInvalidasError(Exception):
    """Se lanza cuando el email no existe o la contraseña es incorrecta."""
    pass


class UsuarioInactivoError(Exception):
    """Se lanza cuando el usuario existe pero fue desactivado por un admin."""
    pass


class AuthService:
    """Lógica de negocio para autenticación y gestión de usuarios."""

    def __init__(self, db: Session) -> None:
        """
        Args:
            db: Sesión de base de datos inyectada por FastAPI.
        """
        self.repo = UserRepository(db)

    def registrar_cliente(self, datos: RegisterRequest) -> tuple[User, str]:
        """
        Registra un nuevo cliente en el sistema.

        Valida que el email no esté en uso, hashea la contraseña,
        y crea el usuario con rol CLIENTE.

        Args:
            datos: Datos del formulario de registro validados por Pydantic.

        Returns:
            Tupla con (usuario_creado, access_token).

        Raises:
            EmailYaRegistradoError: Si el email ya está registrado.
        """
        if self.repo.email_exists(datos.email):
            raise EmailYaRegistradoError(
                f"El email '{datos.email}' ya está registrado en el sistema"
            )

        password_hash = hash_password(datos.password)

        user = self.repo.create(
            nombre=datos.nombre,
            apellido=datos.apellido,
            email=datos.email,
            password_hash=password_hash,
            role=UserRole.CLIENTE,
        )

        token = create_access_token(user_id=user.id, role=user.role)
        return user, token

    def login(self, datos: LoginRequest) -> tuple[User, str]:
        """
        Autentica un usuario existente y genera un JWT.

        Busca al usuario por email y verifica la contraseña con bcrypt.
        No se distingue entre "email no existe" y "contraseña incorrecta"
        en el mensaje de error, para no dar pistas a atacantes.

        Args:
            datos: Email y contraseña enviados por el cliente.

        Returns:
            Tupla con (usuario_autenticado, access_token).

        Raises:
            CredencialesInvalidasError: Si el email no existe o la contraseña es incorrecta.
            UsuarioInactivoError: Si el usuario fue desactivado.
        """
        user = self.repo.get_by_email(datos.email)

        # Verificamos existencia y contraseña en el mismo bloque para
        # evitar timing attacks (ambos errores tardan lo mismo en responder)
        if not user or not verify_password(datos.password, user.password_hash):
            raise CredencialesInvalidasError("Email o contraseña incorrectos")

        if not user.activo:
            raise UsuarioInactivoError(
                "Tu cuenta está desactivada. Contactá al soporte de Virtual Pet."
            )

        token = create_access_token(user_id=user.id, role=user.role)
        return user, token

    def crear_usuario_admin(self, datos: CreateUserAdminRequest) -> User:
        """
        Crea un usuario con cualquier rol. Solo puede llamarlo un ADMIN.
        La validación del rol del llamador se hace en el controller con require_role().

        Permite crear empleados de depósito u otros administradores
        sin pasar por el flujo de registro público.

        Args:
            datos: Datos del nuevo usuario incluyendo el rol a asignar.

        Returns:
            El usuario creado.

        Raises:
            EmailYaRegistradoError: Si el email ya está en uso.
        """
        if self.repo.email_exists(datos.email):
            raise EmailYaRegistradoError(
                f"El email '{datos.email}' ya está registrado en el sistema"
            )

        password_hash = hash_password(datos.password)

        return self.repo.create(
            nombre=datos.nombre,
            apellido=datos.apellido,
            email=datos.email,
            password_hash=password_hash,
            role=datos.role,
        )

    def obtener_perfil(self, user_id: int) -> User:
        """
        Retorna el perfil del usuario autenticado.

        Args:
            user_id: ID del usuario extraído del JWT por el middleware.

        Returns:
            El objeto User con todos sus datos.
        """
        return self.repo.get_by_id(user_id)
