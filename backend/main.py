from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
import traceback
from database import get_db, check_database_connection, check_database_connection_direct

from routers.users import router as users_router

app = FastAPI(title="Pool Banorte API", version="1.0.0")

# Configuración de CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)


@app.get("/")
def read_root():
    return {"message": "Pool Banorte API está funcionando"}

@app.get("/health")
def health_check():
    """Endpoint para verificar el estado de la API y la base de datos"""
    print("[DEBUG] Iniciando health check...")
    
    try:
        # Probar conexión con SQLAlchemy
        print("[DEBUG] === Probando conexión con SQLAlchemy ===")
        db_status_sqlalchemy = check_database_connection()
        print(f"[DEBUG] Resultado SQLAlchemy: {db_status_sqlalchemy}")
        
        # Probar conexión directa con psycopg2
        print("[DEBUG] === Probando conexión directa con psycopg2 ===")
        db_status_direct = check_database_connection_direct()
        print(f"[DEBUG] Resultado psycopg2 directo: {db_status_direct}")
        
        # Determinar estado general
        db_connected = db_status_sqlalchemy or db_status_direct
        
        response = {
            "status": "healthy" if db_connected else "unhealthy",
            "database": "connected" if db_connected else "disconnected",
            "message": "API funcionando correctamente" if db_connected else "Problema con la conexión a la base de datos",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "database_url_prefix": os.getenv("DATABASE_URL", "")[:20] + "..." if os.getenv("DATABASE_URL") else "No configurada",
            "connection_tests": {
                "sqlalchemy": "success" if db_status_sqlalchemy else "failed",
                "psycopg2_direct": "success" if db_status_direct else "failed"
            }
        }
        
        if not db_connected:
            response["error_details"] = "Ambos métodos de conexión fallaron. Revisar logs para detalles."
        elif db_status_direct and not db_status_sqlalchemy:
            response["note"] = "Conexión directa funciona, pero SQLAlchemy falla. Problema de configuración de pool."
        
        return response
        
    except Exception as e:
        print(f"[ERROR] Error en health check: {e}")
        traceback.print_exc()
        return {
            "status": "error",
            "database": "error",
            "message": f"Error interno en health check: {str(e)}",
            "environment": os.getenv("ENVIRONMENT", "development")
        }

@app.get("/health-simple")
def health_check_simple():
    """Endpoint de salud simple sin verificación de base de datos"""
    return {
        "status": "healthy",
        "message": "API funcionando correctamente",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

@app.get("/debug-env")
def debug_environment():
    """Endpoint para verificar variables de entorno (sin valores sensibles)"""
    return {
        "environment": os.getenv("ENVIRONMENT", "not_set"),
        "pythonpath": os.getenv("PYTHONPATH", "not_set"),
        "database_url_configured": "yes" if os.getenv("DATABASE_URL") else "no",
        "database_url_prefix": os.getenv("DATABASE_URL", "")[:30] + "..." if os.getenv("DATABASE_URL") else "not_set",
        "supabase_anon_key_configured": "yes" if os.getenv("SUPABASE_ANON_KEY") else "no",
        "supabase_service_key_configured": "yes" if os.getenv("SUPABASE_SERVICE_KEY") else "no",
        "secret_key_configured": "yes" if os.getenv("SECRET_KEY") else "no",
        "allowed_origins": os.getenv("ALLOWED_ORIGINS", "not_set"),
        "algorithm": os.getenv("ALGORITHM", "not_set"),
        "access_token_expire_minutes": os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "not_set")
    }

@app.post("/debug-create-user")
def debug_create_user(db: Session = Depends(get_db)):
    """Endpoint de debug para probar la creación de usuarios"""
    try:
        print("[DEBUG] === Iniciando debug de creación de usuario ===")
        
        # Importar dependencias
        from services.user_services import UserService
        from schemas.user_schemas import UserCreate
        import uuid
        
        print("[DEBUG] Dependencias importadas correctamente")
        
        # Crear datos de prueba
        test_user_data = UserCreate(
            email=f"debug-{uuid.uuid4()}@example.com",
            name="Debug User",
            password="password123"
        )
        
        print(f"[DEBUG] Datos de usuario creados: {test_user_data.email}")
        
        # Intentar crear usuario
        print("[DEBUG] Llamando a UserService.create_user...")
        created_user = UserService.create_user(db, test_user_data)
        
        print(f"[DEBUG] Usuario creado exitosamente: {created_user.id}")
        
        return {
            "status": "success",
            "message": "Usuario creado exitosamente en modo debug",
            "user_id": str(created_user.id),
            "user_email": created_user.email,
            "user_name": created_user.name
        }
        
    except Exception as e:
        print(f"[ERROR] Error en debug_create_user: {e}")
        traceback.print_exc()
        return {
            "status": "error",
            "message": f"Error al crear usuario: {str(e)}",
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)