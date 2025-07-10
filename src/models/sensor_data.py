from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class SensorType(str, Enum):
    TEMPERATURE = "temperatura"
    HUMIDITY = "humedad"
    CO2 = "CO2"

class SensorData(BaseModel):
    timestamp: datetime
    sensor_id: str # Identificador del sensor Ej:"sensor1", "sensor2", etc.
    value: float # Valor del sensor, por ejemplo, 23.5 para temperatura
    type: SensorType # Tipo de sensor definido en SensorType
    device_id: Optional[str] = None  # ID del dispositivo Arduino/ESP32 o puede omitirse por defecto
    metadata: Optional[dict] = None  # Alg'un otro dato adicional