from fastapi import FastAPI
from src.api.routers import sensors
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Astroflora APP",
    description="APP para ingesta de datos de sensores desde dispositivos Arduino/ESP32",
    version="0.1.0"
)

# Configuración de CORS
origins = [
    "http://localhost:5173",  # URL del frontend React
    "http://127.0.0.1:5173",  # Alternativa
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sensors.router, prefix="/sensors", tags=["sensors"])