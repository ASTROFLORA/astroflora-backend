from sqlalchemy import insert
from src.models.sensor_event import SensorEvent
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class EventStoreService:
    def __init__(self, session):
        self.session = session

    async def save_event(self, data: dict):
        try:
            stmt = insert(SensorEvent).values(
                sensor_id=data.get("sensor_id", "default"),
                temperatura=float(data["temperatura"]),
                humedad=float(data["humedad"]),
                co2=int(data["co2"]),
                presion=float(data["presion"]),
                timestamp=datetime.fromisoformat(data["timestamp"])
            )
            await self.session.execute(stmt)
            await self.session.commit()
            logger.info(f"Evento insertado correctamente: {data}")
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error guardando evento: {e}")
            raise e
