from pydantic import BaseModel
from datetime import datetime


class Weather_Response(BaseModel):
    city: str
    temperature: float
    description: str
    timestamp: datetime


class Config:
    orm_mode = True