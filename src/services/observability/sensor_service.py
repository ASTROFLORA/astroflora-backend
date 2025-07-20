from src.models.orm import SensorEvent
from src.models.dto import SensorData
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.observability.connection import ConnectionManager

class SensorService:
    def __init__(self, db: AsyncSession, connection_manager: ConnectionManager):
        self.db = db
        self.connection_manager = connection_manager

    async def ingest_full_sensor_data(self, data: SensorData):
        event = SensorEvent(
            sensor_id=data.sensor_id,
            timestamp=data.timestamp,
            temperatura=data.temperatura,
            humedad=data.humedad,
            co2=data.co2,
            presion=data.presion
        )
        self.db.add(event)
        await self.db.commit()
        await self.connection_manager.broadcast({
            "sensor_id": data.sensor_id,
            "timestamp": data.timestamp.isoformat(),
            "temperatura": data.temperatura,
            "humedad": data.humedad,
            "co2": data.co2,
            "presion": data.presion
        })
