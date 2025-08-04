from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import engine, Base, get_db, check_database_connection
from config import settings
import os

# Crear la aplicación FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Pool Banorte API is running",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": settings.APP_VERSION
    }

@app.get("/health")
async def health_check():
    """Endpoint para verificar el estado de la aplicación y la base de datos"""
    try:
        # Usar la función optimizada para verificar conexión
        db_connected = check_database_connection()
        
        if db_connected:
            return {
                "status": "healthy",
                "database": "connected",
                "app_name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": os.getenv("ENVIRONMENT", "development")
            }
        else:
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "app_name": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "environment": os.getenv("ENVIRONMENT", "development"),
                "error": "Database connection failed"
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "error": str(e)
        }

@app.get("/health-simple")
async def health_simple():
    """Endpoint simple sin verificación de base de datos"""
    return {
        "status": "healthy",
        "message": "API is running",
        "environment": os.getenv("ENVIRONMENT", "development")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)