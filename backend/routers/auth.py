from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from database import get_db
from schemas.user_schemas import UserCreate, UserLogin, Token, UserResponseWithToken, UserResponse
from services.user_services import UserService
from utils.auth import ACCESS_TOKEN_EXPIRE_MINUTES, verify_password, create_access_token
from dependencies.auth import get_current_user

router = APIRouter(prefix="/auth", tags=["autenticación"])

@router.post("/register", response_model=UserResponseWithToken, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Registrar un nuevo usuario en el sistema
    
    - **email**: Email único del usuario
    - **name**: Nombre completo del usuario  
    - **password**: Contraseña (mínimo 8 caracteres, debe contener letras y números)
    
    Retorna el usuario creado junto con su token de acceso.
    """
    # Verificar si el email ya existe
    existing_user = UserService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado en el sistema"
        )
    
    # Crear el nuevo usuario
    try:
        new_user = UserService.create_user(db, user_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el usuario: {str(e)}"
        )
    
    # Generar token de acceso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email, "user_id": str(new_user.id)},
        expires_delta=access_token_expires
    )
    
    # Retornar usuario con token
    return UserResponseWithToken(
        id=new_user.id,
        email=new_user.email,
        name=new_user.name,
        created_at=new_user.created_at,
        updated_at=new_user.updated_at,
        access_token=access_token,
        token_type="bearer"
    )

@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Autenticar usuario con formulario OAuth2 (para compatibilidad con Swagger UI)
    
    - **username**: Email del usuario
    - **password**: Contraseña del usuario
    
    Retorna un token de acceso JWT.
    """
    user = UserService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login-json", response_model=Token)
async def login_json(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Autenticar usuario con JSON
    
    - **email**: Email del usuario
    - **password**: Contraseña del usuario
    
    Retorna un token de acceso JWT.
    """
    user = UserService.authenticate_user(db, user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user = Depends(get_current_user)):
    """
    Obtener información del usuario autenticado actual
    
    Requiere token de autenticación válido.
    """
    return current_user