from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import crear_tablas
from app.routers import usuarios_router, examenes_router

# Crear tablas al iniciar
crear_tablas()

# Crear la aplicación
app = FastAPI(
    title="API de Exámenes Médicos",
    description="API para gestión de exámenes médicos con autenticación JWT",
    version="2.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True,
        "displayRequestDuration": True,
    }
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers
app.include_router(usuarios_router)
app.include_router(examenes_router)

# Endpoint raíz
@app.get("/")
def root():
    return {
        "mensaje": "API de Exámenes Médicos funcionando 🏥",
        "version": "2.0.0",
        "endpoints": {
            "documentacion": "/docs",
            "redoc": "/redoc"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)