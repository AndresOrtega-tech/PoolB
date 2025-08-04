from sqlalchemy import create_engine
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
    # Configuración optimizada para PostgreSQL en serverless
    engine = create_engine(
        DATABASE_URL,
        pool_size=1,  # Reducir el pool size para serverless
        max_overflow=0,  # Sin overflow en serverless
        pool_pre_ping=True,  # Verificar conexiones antes de usar
        pool_recycle=300,  # Reciclar conexiones cada 5 minutos
        connect_args={
            "connect_timeout": 10,
            "application_name": "pool_banorte_api"
        }
    )
else:
    # Configuración para SQLite (desarrollo local)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

# Crear SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear Base class
Base = declarative_base()

# Dependency para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()