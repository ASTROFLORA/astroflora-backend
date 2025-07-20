from src.db.database import Base
from sqlalchemy import Column, Integer, Float, Text, TIMESTAMP, String

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False) 

class SensorEvent(Base):
    __tablename__ = "sensor_events"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Text, default="default")
    temperatura = Column(Float, nullable=False)
    humedad = Column(Float, nullable=False)
    co2 = Column(Integer, nullable=False)
    presion = Column(Float, nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)