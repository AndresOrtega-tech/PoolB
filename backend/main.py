from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from database import engine, Base, get_db
from config import settings

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

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
    return {"message": "Pool Banorte API is running"}

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Endpoint para verificar el estado de la aplicación y la base de datos"""
    try:
        # Intentar hacer una consulta simple a la base de datos
        result = db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
        
@app.get("/init-db")
async def init_db(db: Session = Depends(get_db)):
    """Endpoint para inicializar la base de datos"""
    try:
        # Crear las tablas en la base de datos
        Base.metadata.create_all(bind=engine)
        return {"message": "Base de datos inicializada correctamente"}
    except Exception as e:
        return {"error": f"Error al inicializar la base de datos: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    Base.metadata.create_all(bind=engine)
    uvicorn.run(app, host="0.0.0.0", port=8000)