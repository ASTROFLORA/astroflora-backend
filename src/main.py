from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import sensors
from contextlib import asynccontextmanager
import asyncio
import random
from datetime import datetime
import logging
from typing import Optional
from src.services.event_store import EventStoreService
from src.db.database import get_async_session, Base, engine
from src.auth.router import router as auth_router
import dotenv

dotenv.load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections = []
        self.data_generator_task: Optional[asyncio.Task] = None
        self._stop_event = asyncio.Event()
        self.event_store: Optional[EventStoreService] = None
    
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

    async def start_data_generator(self, event_store: EventStoreService):
        self._stop_event.clear()
        self.event_store = event_store
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
        while not self._stop_event.is_set():
            try:
                data = {
                    "temperatura": round(random.uniform(15.0, 35.0), 2),
                    "humedad": round(random.uniform(30.0, 90.0), 2),
                    "co2": int(round(random.uniform(300.0, 2000.0))),
                    "presion": round(random.uniform(0.0, 20.0), 2),
                    "timestamp": datetime.now().isoformat()
                }

                # Guardar en la base de datos
                if self.event_store:
                    await self.event_store.save_event({
                        "temperatura": data["temperatura"],
                        "humedad": data["humedad"],
                        "co2": data["co2"],
                        "presion": data["presion"],
                        "timestamp": data["timestamp"]
                    })

                await self.broadcast(data)

                try:
                    await asyncio.wait_for(asyncio.sleep(30), timeout=30.0)
                except asyncio.TimeoutError:
                    continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error en generador de datos: {e}")
                await asyncio.sleep(1)

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear sesión para el EventStoreService
    from src.db.database import async_session
    session = async_session()
    event_store = EventStoreService(await session.__aenter__())  # obtener la sesión async
    await manager.start_data_generator(event_store)
    logger.info("Aplicación iniciada - Servicio de generación de datos activo")

    yield

    await manager.stop_data_generator()
    await session.__aexit__(None, None, None)
    logger.info("Aplicación detenida - Limpieza completada")
    
app = FastAPI(
    title="Astroflora APP",
    description="APP para ingesta de datos de sensores desde dispositivos Arduino/ESP32",
    version="0.1.0",
    lifespan=lifespan
)

# Configuración de CORS
origins = [
    "http://localhost:3000",
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
app.include_router(auth_router)

# Crear tablas al iniciar
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


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