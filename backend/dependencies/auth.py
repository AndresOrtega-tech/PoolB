"""
Dependencias de autenticación para FastAPI

Este módulo contiene las dependencias que se usan para proteger endpoints
que requieren autenticación JWT.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import get_db
from services.user_services import UserService
from utils.auth import verify_token
from models import User

# OAuth2 scheme para extraer tokens de los headers
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> User:
    """
    Dependencia para obtener el usuario actual desde el token JWT
    
    Esta función se usa como dependencia en endpoints protegidos.
    Extrae el token del header Authorization, lo verifica y retorna
    el usuario correspondiente.
    
    Args:
        token: Token JWT extraído del header Authorization
        db: Sesión de base de datos
        
    Returns:
        User: Usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verify_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
    
    user = UserService.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependencia para obtener el usuario actual activo
    
    Esta función extiende get_current_user para verificar que el usuario
    esté activo (si implementamos un campo is_active en el futuro).
    
    Args:
        current_user: Usuario actual obtenido de get_current_user
        
    Returns:
        User: Usuario autenticado y activo
        
    Raises:
        HTTPException: Si el usuario está inactivo
    """
    # Por ahora todos los usuarios están activos
    # En el futuro se puede agregar verificación de is_active
    return current_user