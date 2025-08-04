from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pool_banorte.db")

# Configuración específica para serverless (Vercel)
if "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
    # Configuración optimizada para PostgreSQL/Supabase en serverless
    engine = create_engine(
        DATABASE_URL,
        pool_size=1,  # Mínimo pool para serverless
        max_overflow=0,  # Sin conexiones adicionales
        pool_pre_ping=True,  # Verificar conexiones
        pool_recycle=3600,  # Reciclar cada hora
        pool_timeout=20,  # Timeout de 20 segundos
        echo=False,  # Desactivar logs SQL en producción
        connect_args={
            "connect_timeout": 20,
            "application_name": "pool_banorte_vercel",
            "sslmode": "require",  # SSL requerido para Supabase
            "target_session_attrs": "read-write"
        }
    )
else:
    # Configuración para SQLite (desarrollo local)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=True  # Activar logs SQL en desarrollo
    )

# Crear SessionLocal class con configuración optimizada
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False  # Evitar problemas con objetos después del commit
)

# Crear Base class
Base = declarative_base()

# Dependency para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para verificar la conexión a la base de datos
def check_database_connection():
    """Función para verificar si la conexión a la base de datos está funcionando"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"Error de conexión a la base de datos: {e}")
        return False