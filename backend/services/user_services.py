from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from uuid import UUID
import uuid

from models import User
from schemas.user_schemas import UserCreate, UserUpdate

# Importar hash_password con manejo de errores para Vercel
try:
    from utils.auth import hash_password
    BCRYPT_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] bcrypt no disponible: {e}")
    BCRYPT_AVAILABLE = False
    
    def hash_password(password: str) -> str:
        """Fallback hash function si bcrypt no está disponible"""
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

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
        try:
            hashed_password = hash_password(user_data.password)
            print(f"[DEBUG] Password hashed successfully, bcrypt available: {BCRYPT_AVAILABLE}")
        except Exception as e:
            print(f"[ERROR] Error hashing password: {e}")
            # Fallback a hash simple si bcrypt falla
            import hashlib
            hashed_password = hashlib.sha256(user_data.password.encode()).hexdigest()
            print("[WARNING] Using SHA256 fallback for password")
        
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
            try:
                update_data['password'] = hash_password(update_data['password'])
                print(f"[DEBUG] Password updated and hashed, bcrypt available: {BCRYPT_AVAILABLE}")
            except Exception as e:
                print(f"[ERROR] Error hashing updated password: {e}")
                # Fallback a hash simple si bcrypt falla
                import hashlib
                update_data['password'] = hashlib.sha256(update_data['password'].encode()).hexdigest()
                print("[WARNING] Using SHA256 fallback for updated password")
        
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




