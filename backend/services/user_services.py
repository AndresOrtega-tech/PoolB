from sqlalchemy.orm import Session
from models import User
from schemas.user_schemas import UserCreate, UserCreateDB, UserUpdate, UserUpdateDB
from utils.auth import hash_password, verify_password
from typing import Optional, List
from uuid import UUID
import uuid

class UserService:
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtener lista de usuarios con paginación"""
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """Obtener usuario por ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Crear un nuevo usuario con contraseña hasheada"""
        # Hashear la contraseña antes de guardarla
        hashed_password = hash_password(user_data.password)
        
        db_user = User(
            id=uuid.uuid4(),
            email=user_data.email,
            name=user_data.name,
            password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update_user(db: Session, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
        """Actualizar un usuario existente"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        
        # Si se está actualizando la contraseña, hashearla
        if 'password' in update_data and update_data['password'] is not None:
            update_data['password'] = hash_password(update_data['password'])
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: UUID) -> bool:
        """Eliminar un usuario"""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Autenticar un usuario verificando email y contraseña
        
        Args:
            db: Sesión de base de datos
            email: Email del usuario
            password: Contraseña en texto plano
            
        Returns:
            User si las credenciales son válidas, None en caso contrario
        """
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
            
        if not verify_password(password, user.password):
            return None
        
        return user
    
    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """
        Registrar un nuevo usuario
        
        Args:
            db: Sesión de base de datos
            user_data: Datos del usuario a crear
            
        Returns:
            User creado
            
        Raises:
            ValueError: Si el email ya está registrado
        """
        existing_user = UserService.get_user_by_email(db, user_data.email)
        if existing_user:
            raise ValueError("El email ya está registrado en el sistema")
        
        return UserService.create_user(db, user_data)



