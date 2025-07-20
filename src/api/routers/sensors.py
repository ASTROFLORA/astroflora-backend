from fastapi import APIRouter, Depends, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio
from src.models.orm import SensorEvent
from src.models.dto import SensorData
from src.services.observability.sensor_service import SensorService
from src.api.dependencies import get_db, get_connection_manager, get_async_session
from src.services.observability.connection import ConnectionManager

router = APIRouter()
manager = ConnectionManager()

@router.post("/ingest", status_code=status.HTTP_204_NO_CONTENT)
async def ingest_sensor_payload(
    data: SensorData,
    db: AsyncSession = Depends(get_db),
    connection_manager: ConnectionManager = Depends(get_connection_manager),
):
    service = SensorService(db, connection_manager)
    await service.ingest_full_sensor_data(data)



@router.websocket("/ws/sensors/live")
async def websocket_sensor_data(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            async with get_async_session() as session:
                result = await session.execute(
                    select(SensorEvent)
                    .order_by(SensorEvent.timestamp.desc())
                    .limit(1)
                )
                event = result.scalars().first()

                if event:
                    # Solo incluir sensores que tienen datos
                    data = {
                        "id": str(event.id),
                        "sensor_id": event.sensor_id,
                        "timestamp": event.timestamp.isoformat(),
                    }

                    if event.temperatura is not None:
                        data["temperatura"] = event.temperatura
                    if event.humedad is not None:
                        data["humedad"] = event.humedad
                    if event.co2 is not None:
                        data["co2"] = event.co2
                    if event.presion is not None:
                        data["presion"] = event.presion

                    await websocket.send_json(data)

            await asyncio.sleep(2)  # cada 2 segundos
    except WebSocketDisconnect:
        manager.disconnect(websocket)
