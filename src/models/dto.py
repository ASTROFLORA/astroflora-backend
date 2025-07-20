from pydantic import BaseModel
from datetime import datetime

class SensorData(BaseModel):
    sensor_id: str
    timestamp: datetime  # Mantiene zona horaria si se incluye correctamente en JSON
    temperatura: float
    humedad: float
    co2: float
    presion: float
