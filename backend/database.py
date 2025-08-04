from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import traceback
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pool_banorte.db")

print(f"[DEBUG] DATABASE_URL configurada: {DATABASE_URL[:50]}...")  # Solo primeros 50 caracteres por seguridad

# Configuración específica para serverless (Vercel)
if "postgresql" in DATABASE_URL or "postgres" in DATABASE_URL:
    print("[DEBUG] Configurando engine para PostgreSQL/Supabase")
    
    # Configuración específica para Vercel serverless + Supabase
    engine = create_engine(
        DATABASE_URL,
        # Pool configuration para serverless
        pool_size=0,  # No mantener conexiones persistentes
        max_overflow=0,  # Sin overflow
        pool_pre_ping=False,  # Desactivar pre-ping en serverless
        pool_recycle=-1,  # No reciclar conexiones
        pool_timeout=30,  # Timeout más largo
        echo=False,  # Sin logs SQL
        # Configuración de conexión optimizada para Supabase
        connect_args={
            "connect_timeout": 30,  # Timeout más largo
            "command_timeout": 30,
            "application_name": "pool_banorte_vercel",
            "sslmode": "require",  # SSL obligatorio
            "sslcert": None,
            "sslkey": None,
            "sslrootcert": None,
            "options": "-c timezone=UTC -c statement_timeout=30000",
            # Forzar IPv4 para evitar problemas de IPv6 en Vercel
            "host": DATABASE_URL.split("@")[1].split(":")[0] if "@" in DATABASE_URL else None,
        }
    )
    print("[DEBUG] Engine PostgreSQL configurado exitosamente")
else:
    print("[DEBUG] Configurando engine para SQLite")
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
        print("[DEBUG] Intentando conectar a la base de datos...")
        with engine.connect() as connection:
            print("[DEBUG] Conexión establecida, ejecutando SELECT 1...")
            result = connection.execute(text("SELECT 1"))
            print("[DEBUG] Query ejecutada exitosamente")
            return True
    except Exception as e:
        print(f"[ERROR] Error de conexión a la base de datos: {e}")
        print(f"[ERROR] Tipo de error: {type(e).__name__}")
        print(f"[ERROR] Traceback completo:")
        traceback.print_exc()
        return False

# Función alternativa para conexión directa (sin pool) en serverless
def check_database_connection_direct():
    """Función alternativa que usa conexión directa sin pool para serverless"""
    import psycopg2
    from urllib.parse import urlparse
    
    try:
        print("[DEBUG] Intentando conexión directa con psycopg2...")
        
        # Parsear la DATABASE_URL
        parsed = urlparse(DATABASE_URL)
        
        # Configuración de conexión directa
        conn_params = {
            "host": parsed.hostname,
            "port": parsed.port or 5432,
            "database": parsed.path[1:],  # Remover el '/' inicial
            "user": parsed.username,
            "password": parsed.password,
            "sslmode": "require",
            "connect_timeout": 30,
        }
        
        print(f"[DEBUG] Conectando a host: {conn_params['host']}:{conn_params['port']}")
        
        # Intentar conexión directa
        with psycopg2.connect(**conn_params) as conn:
            with conn.cursor() as cursor:
                print("[DEBUG] Ejecutando SELECT 1 con psycopg2...")
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                print(f"[DEBUG] Resultado: {result}")
                return True
                
    except Exception as e:
        print(f"[ERROR] Error en conexión directa: {e}")
        print(f"[ERROR] Tipo de error: {type(e).__name__}")
        traceback.print_exc()
        return False