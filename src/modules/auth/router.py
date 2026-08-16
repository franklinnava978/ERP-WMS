import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db_session
from src.core.middleware.tenant import get_tenant_db_session, oauth2_scheme
from src.core.security import decode_token
from src.modules.auth.schemas import UserCreate, UserResponse, LoginRequest, TokenResponse
from src.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticación & Usuarios"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Registra un nuevo usuario asignado a un Tenant específico."""
    return await AuthService.register_user(db, payload)

@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """Autentica un usuario contra su tenant y retorna el token JWT."""
    return await AuthService.login(db=db, dto=payload)

@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_tenant_db_session)
):
    """Retorna la información del usuario autenticado en su contexto Multi-Tenant."""
    payload = decode_token(token)
    user_id = uuid.UUID(payload.get("sub"))
    return await AuthService.get_current_user(db, user_id)