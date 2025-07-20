from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class SensorType(str, Enum):
    TEMPERATURE = "temperatura"
    HUMIDITY = "humedad"
    CO2 = "CO2"
    PRESSURE = "presion"

class SensorData(BaseModel):
    timestamp: datetime
    sensor_id: str
    value: float
    type: SensorType
    device_id: Optional[str] = None
    metadata: Optional[dict] = None