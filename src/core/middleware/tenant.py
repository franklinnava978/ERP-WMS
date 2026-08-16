from typing import AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_db_session, set_tenant_session
from src.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_tenant_db_session(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session)
) -> AsyncGenerator[AsyncSession, None]:
    """Valida el token JWT, aplica SET LOCAL tenant_id en PostgreSQL y retorna la sesión aislada."""
    payload = decode_token(token)
    tenant_id = payload.get("tenant_id")
    
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o sin contexto de Tenant",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Inyecta el tenant_id en la transacción PostgreSQL
    await set_tenant_session(db, tenant_id)
    yield db