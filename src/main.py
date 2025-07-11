from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import sensors
from contextlib import asynccontextmanager
import asyncio
import random
from datetime import datetime
import logging
from typing import Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections = []
        self.data_generator_task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Nueva conexión WebSocket. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Conexión cerrada. Total: {len(self.active_connections)}")
    
    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(data)
            except Exception as e:
                logger.error(f"Error enviando datos: {e}")
                self.disconnect(connection)

    async def start_data_generator(self):
        """Inicia la tarea de generación de datos"""
        if self.data_generator_task is None or self.data_generator_task.done():
            self._stop_event.clear()
            self.data_generator_task = asyncio.create_task(self._generate_sensor_data())
            logger.info("Generador de datos iniciado")
    
    async def stop_data_generator(self):
        """Detiene la tarea de generación de datos"""
        if self.data_generator_task and not self.data_generator_task.done():
            self._stop_event.set()
            self.data_generator_task.cancel()
            try:
                # Esperar un tiempo razonable para que la tarea se cancele
                await asyncio.wait_for(self.data_generator_task, timeout=2.0)
            except asyncio.TimeoutError:
                logger.warning("Tiempo de espera agotado al cancelar generador")
            except asyncio.CancelledError:
                logger.info("Generador de datos cancelado correctamente")
            except Exception as e:
                logger.error(f"Error al detener generador: {e}")
            finally:
                self.data_generator_task = None

    async def _generate_sensor_data(self):
        """Generador real de datos de sensores"""
        while not self._stop_event.is_set():
            try:
                data = {
                    "temperatura": round(random.uniform(15.0, 35.0), 2),
                    "humedad": round(random.uniform(30.0, 90.0), 2),
                    "CO2": round(random.uniform(300.0, 2000.0)),
                    "presion": round(random.uniform(0.0, 20.0), 2),
                    "timestamp": datetime.now().isoformat()
                }
                logger.debug(f"Generando datos: {data}")
                await self.broadcast(data)
                
                # Espera con posibilidad de cancelación
                try:
                    await asyncio.wait_for(
                        asyncio.sleep(5),
                        timeout=5.0
                    )
                except asyncio.TimeoutError:
                    continue  # Normalmente no debería ocurrir
                
            except asyncio.CancelledError:
                logger.info("Generador de datos recibió señal de cancelación")
                break
            except Exception as e:
                logger.error(f"Error en generador de datos: {e}")
                await asyncio.sleep(1)  # Esperar antes de reintentar

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Iniciar el generador de datos al arrancar
    await manager.start_data_generator()
    logger.info("Aplicación iniciada - Servicio de generación de datos activo")
    
    yield  # La aplicación está en ejecución
    
    # Limpieza al detener
    await manager.stop_data_generator()
    logger.info("Aplicación detenida - Limpieza completada")

app = FastAPI(
    title="Astroflora APP",
    description="APP para ingesta de datos de sensores desde dispositivos Arduino/ESP32",
    version="0.1.0",
    lifespan=lifespan
)

# Configuración de CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "ws://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sensors.router, prefix="/sensors", tags=["sensors"])

@app.websocket("/ws/sensors")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Mantener la conexión activa
            data = await websocket.receive_text()
            logger.debug(f"Mensaje recibido: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"Error en WebSocket: {e}")
        manager.disconnect(websocket)