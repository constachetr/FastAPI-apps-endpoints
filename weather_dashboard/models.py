from sqlalchemy import Column, Integer, Float, DateTime, String
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


Base = declarative_base()


class Weather(Base):
    __tablename__ = "weather"
    id = Column(Integer, primary_key=True, autoincrement=True)
    city = Column(String, index=True)
    temperature = Column(Float)
    description = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow())