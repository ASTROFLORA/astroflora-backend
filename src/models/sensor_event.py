from sqlalchemy import Column, Integer, Float, Text, TIMESTAMP, String
from sqlalchemy.ext.declarative import declarative_base
from src.db.database import Base


class SensorEvent(Base):
    __tablename__ = "sensor_events"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Text, default="default")
    temperatura = Column(Float, nullable=False)
    humedad = Column(Float, nullable=False)
    co2 = Column(Integer, nullable=False)
    presion = Column(Float, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
