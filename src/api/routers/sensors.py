from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.dto import SensorData
from src.services.observability.sensor_service import SensorService
from src.api.dependencies import get_db, get_connection_manager
from src.services.observability.connection import ConnectionManager

router = APIRouter()

@router.post("/ingest", status_code=status.HTTP_204_NO_CONTENT)
async def ingest_sensor_payload(
    data: SensorData,
    db: AsyncSession = Depends(get_db),
    connection_manager: ConnectionManager = Depends(get_connection_manager),
):
    service = SensorService(db, connection_manager)
    await service.ingest_full_sensor_data(data)
