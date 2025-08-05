from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from schemas.user_schemas import UserCreate, UserUpdate, UserResponse
from services.user_services import UserService

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Listar usuarios con paginación"""
    users = UserService.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: UUID, db: Session = Depends(get_db)):
    """Obtener usuario por ID"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Crear nuevo usuario"""
    # Verificar si el email ya existe
    existing_user = UserService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    return UserService.create_user(db, user_data)

@router.put("/{user_id}", response_model=UserResponse)
def update_user_complete(user_id: UUID, user_data: UserCreate, db: Session = Depends(get_db)):
    """Actualizar usuario completo"""
    user = UserService.update_user(db, user_id, UserUpdate(**user_data.dict()))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user

@router.patch("/{user_id}", response_model=UserResponse)
def update_user_partial(user_id: UUID, user_data: UserUpdate, db: Session = Depends(get_db)):
    """Actualizar usuario parcial"""
    user = UserService.update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, db: Session = Depends(get_db)):
    """Eliminar usuario"""
    success = UserService.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )