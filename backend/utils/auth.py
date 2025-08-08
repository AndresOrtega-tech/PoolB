import bcrypt
from typing import Optional
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status
import os

# Configuración para JWT (con valores por defecto si no están en .env)
SECRET_KEY = os.getenv("SECRET_KEY", "tu_clave_secreta_super_segura_aqui_cambiar_en_produccion")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

class PasswordManager:
    """Clase para manejar el hash y verificación de contraseñas con bcrypt"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Genera un hash bcrypt de la contraseña
        
        Args:
            password (str): Contraseña en texto plano
            
        Returns:
            str: Hash bcrypt de la contraseña
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verifica si una contraseña coincide con su hash
        
        Args:
            plain_password (str): Contraseña en texto plano
            hashed_password (str): Hash almacenado en la base de datos
            
        Returns:
            bool: True si la contraseña es correcta, False en caso contrario
        """
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False

class TokenManager:
    """Clase para manejar tokens JWT"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Crea un token JWT de acceso
        
        Args:
            data (dict): Datos a incluir en el token
            expires_delta (timedelta, optional): Tiempo de expiración personalizado
            
        Returns:
            str: Token JWT
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """
        Verifica y decodifica un token JWT
        
        Args:
            token (str): Token JWT a verificar
            
        Returns:
            dict: Payload del token decodificado
            
        Raises:
            HTTPException: Si el token es inválido o ha expirado
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token ha expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )

# Instancias globales para usar en toda la aplicación
pwd_manager = PasswordManager()
token_manager = TokenManager()

# Funciones de conveniencia
def hash_password(password: str) -> str:
    """Función de conveniencia para hashear contraseñas"""
    return pwd_manager.hash_password(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Función de conveniencia para verificar contraseñas"""
    return pwd_manager.verify_password(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Función de conveniencia para crear tokens"""
    return token_manager.create_access_token(data, expires_delta)

def verify_token(token: str) -> dict:
    """Función de conveniencia para verificar tokens"""
    return token_manager.verify_token(token)

