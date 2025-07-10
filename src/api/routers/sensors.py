from fastapi import APIRouter, HTTPException
from src.models.sensor_data import SensorData, SensorType
from src.services.sensor_data_store import SensorDataStoreService
from typing import Optional
from datetime import datetime, timedelta
import random
from enum import Enum

router = APIRouter()
sensor_store = SensorDataStoreService()

@router.post("/ingest") # /sensors/ingest
async def ingest_sensor_data(sensor_data: SensorData):
    try:
        sensor_store.store_sensor_data(sensor_data)
        return {"status": "success", "message": "Data stored successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/data")
async def get_sensor_data(sensor_id: Optional[str] = None, limit: int = 100, 
                         simulate: bool = False, hours: int = 24):
    """
    Obtiene datos de sensores, con opción para simular datos aleatorios
    
    Parámetros:
    - sensor_id: Filtrar por ID de sensor específico
    - limit: Número máximo de registros a devolver
    - simulate: Si True, genera datos aleatorios en lugar de usar los almacenados
    - hours: Cuando simulate=True, cuántas horas de datos generar (por defecto 24)
    """
    if simulate:
        # Generar datos simulados
        simulated_data = generate_simulated_data(hours=hours, sensor_id=sensor_id)
        
        # Formatear respuesta para el frontend
        response_data = {
            "temperatura": [d for d in simulated_data if d.type == SensorType.TEMPERATURE][:limit],
            "humedad": [d for d in simulated_data if d.type == SensorType.HUMIDITY][:limit],
            "CO2": [d for d in simulated_data if d.type == SensorType.CO2][:limit]
        }
        
        return response_data
    else:
        # Usar datos reales del almacenamiento
        data = sensor_store.get_sensor_data(sensor_id=sensor_id, limit=limit)
        
        if sensor_id is None:
            # Organizar datos por tipo cuando no se filtra por sensor_id
            response_data = {
                "temperatura": [d for d in data if d.type == SensorType.TEMPERATURE],
                "humedad": [d for d in data if d.type == SensorType.HUMIDITY],
                "CO2": [d for d in data if d.type == SensorType.CO2]
            }
            return {"message": "Querying all sensors", "data": response_data}
        else:
            return {"message": f"Querying sensor {sensor_id}", "data": data}

def generate_simulated_data(hours: int = 24, sensor_id: Optional[str] = None) -> list[SensorData]:
    """Genera datos de sensores simulados para testing"""
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)
    interval = timedelta(minutes=5)  # Intervalo entre lecturas
    
    # Configuración de sensores disponibles
    available_sensors = {
        SensorType.TEMPERATURE: ["temp_1", "temp_2", "temp_out"],
        SensorType.HUMIDITY: ["hum_1", "hum_2"],
        SensorType.CO2: ["co2_1"]
    }
    
    # Si se especifica un sensor_id, filtrar los sensores a generar
    if sensor_id:
        filtered_sensors = {}
        for sensor_type, ids in available_sensors.items():
            if sensor_id in ids:
                filtered_sensors[sensor_type] = [sensor_id]
        if not filtered_sensors:
            return []
        available_sensors = filtered_sensors
    
    data = []
    current_time = start_time
    
    while current_time <= end_time:
        for sensor_type, sensor_ids in available_sensors.items():
            for s_id in sensor_ids:
                # Generar valor según el tipo de sensor
                if sensor_type == SensorType.TEMPERATURE:
                    value = round(random.uniform(15.0, 35.0), 2)
                    metadata = {"unit": "°C", "variation": round(random.uniform(0.1, 0.5), 2)}
                elif sensor_type == SensorType.HUMIDITY:
                    value = round(random.uniform(30.0, 90.0), 2)
                    metadata = {"unit": "%", "variation": round(random.uniform(0.5, 1.5), 2)}
                else:  # CO2
                    value = round(random.uniform(300.0, 2000.0))
                    metadata = {"unit": "ppm", "calibrated": random.choice([True, False])}
                
                data.append(SensorData(
                    timestamp=current_time,
                    sensor_id=s_id,
                    value=value,
                    type=sensor_type,
                    device_id=random.choice(["ESP32-001", "ESP32-002", "Arduino-101"]),
                    metadata=metadata
                ))
        
        current_time += interval
    
    # Ordenar por timestamp (más reciente primero)
    data.sort(key=lambda x: x.timestamp, reverse=True)
    
    return data