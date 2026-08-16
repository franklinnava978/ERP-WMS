import uuid
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.security import get_password_hash, verify_password, create_access_token
from src.modules.tenants.models import Tenant
from src.modules.auth.models import User
from src.modules.auth.schemas import UserCreate, LoginRequest, TokenResponse

class AuthService:

    @staticmethod
    async def register_user(db: AsyncSession, dto: UserCreate) -> User:
        tenant = await db.get(Tenant, dto.tenant_id)
        if not tenant or not tenant.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant no encontrado o inactivo."
            )
        
        query = select(User).where(User.tenant_id == dto.tenant_id, User.email == dto.email.lower())
        result = await db.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está registrado en este tenant."
            )

        new_user = User(
            tenant_id=dto.tenant_id,
            email=dto.email.lower(),
            password_hash=get_password_hash(dto.password),
            full_name=dto.full_name.strip()
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user

    @staticmethod
    async def login(db: AsyncSession, dto: LoginRequest) -> TokenResponse:
        tenant_query = select(Tenant).where(Tenant.code == dto.tenant_code.strip().upper())
        tenant_res = await db.execute(tenant_query)
        tenant = tenant_res.scalar_one_or_none()

        if not tenant or not tenant.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas o tenant no disponible."
            )

        user_query = select(User).where(
            User.tenant_id == tenant.id,
            User.email == dto.email.lower()
        )
        user_res = await db.execute(user_query)
        user = user_res.scalar_one_or_none()

        if not user or not user.is_active or not verify_password(dto.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo electrónico o contraseña incorrectos."
            )

        token = create_access_token(subject=str(user.id), tenant_id=str(tenant.id))

        return TokenResponse(
            access_token=token,
            tenant_id=tenant.id,
            user_id=user.id
        )

    @staticmethod
    async def get_current_user(db: AsyncSession, user_id: uuid.UUID) -> User:
        user = await db.get(User, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado o inactivo."
            )
        return user