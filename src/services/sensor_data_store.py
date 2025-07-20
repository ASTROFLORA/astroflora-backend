from typing import List, Optional
from src.models.dto import SensorData

class SensorDataStoreService:
    def __init__(self):
        self._data = []
    
    def store_sensor_data(self, sensor_data: SensorData) -> bool:
        """Almacena datos de sensores en memoria"""
        self._data.append(sensor_data)
        return True
    
    def get_sensor_data(self, sensor_id: Optional[str] = None, limit: int = 100) -> List[SensorData]:
        """Obtiene datos históricos de sensores"""
        filtered_data = self._data
        
        if sensor_id is not None:
            filtered_data = [d for d in filtered_data if d.sensor_id == sensor_id]
        return filtered_data[-limit:]