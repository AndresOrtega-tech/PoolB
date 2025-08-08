from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from uuid import UUID
import uuid

from models import User
from schemas.user_schemas import UserCreate, UserUpdate
# from utils.auth import hash_password  # Comentado temporalmente para debug

class UserService:
    
    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        # Hashear la contraseña antes de guardarla
        # hashed_password = hash_password(user_data.password)  # Comentado temporalmente
        hashed_password = "temp_password_hash"  # Temporal para debug
        
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
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        
        # Si se está actualizando la contraseña, hashearla
        if 'password' in update_data and update_data['password'] is not None:
            # update_data['password'] = hash_password(update_data['password'])  # Comentado temporalmente
            update_data['password'] = "temp_updated_password_hash"  # Temporal para debug
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def delete_user(db: Session, user_id: UUID) -> bool:
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True




