from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from uuid import UUID
from datetime import datetime
import re

class UserBase(BaseModel):
    email: EmailStr
    name: str

class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Contraseña del usuario (mínimo 8 caracteres)"
    )
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra')
        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v

class UserCreateDB(UserBase):
    """Schema interno para crear usuario en DB con password hasheada"""
    password: str  # Este será el hash, no la contraseña original

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=100,
        description="Nueva contraseña del usuario (opcional)"
    )
    
    @validator('password')
    def validate_password(cls, v):
        if v is not None:
            if len(v) < 8:
                raise ValueError('La contraseña debe tener al menos 8 caracteres')
            if not re.search(r'[A-Za-z]', v):
                raise ValueError('La contraseña debe contener al menos una letra')
            if not re.search(r'\d', v):
                raise ValueError('La contraseña debe contener al menos un número')
        return v

class UserUpdateDB(BaseModel):
    """Schema interno para actualizar usuario en DB"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None  # Hash de la contraseña

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., description="Contraseña del usuario")

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserResponseWithToken(UserResponse):
    access_token: str
    token_type: str = "bearer"

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    user_id: Optional[str] = None






