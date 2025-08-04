from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
import traceback
from database import get_db, check_database_connection

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

@app.get("/")
def read_root():
    return {"message": "Pool Banorte API está funcionando"}

@app.get("/health")
def health_check():
    """Endpoint para verificar el estado de la API y la base de datos"""
    print("[DEBUG] Iniciando health check...")
    
    try:
        db_status = check_database_connection()
        print(f"[DEBUG] Resultado de check_database_connection: {db_status}")
        
        response = {
            "status": "healthy" if db_status else "unhealthy",
            "database": "connected" if db_status else "disconnected",
            "message": "API funcionando correctamente" if db_status else "Problema con la conexión a la base de datos",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "database_url_prefix": os.getenv("DATABASE_URL", "")[:20] + "..." if os.getenv("DATABASE_URL") else "No configurada"
        }
        
        if not db_status:
            response["error_details"] = "Revisar logs de Vercel para más detalles del error de conexión"
        
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)