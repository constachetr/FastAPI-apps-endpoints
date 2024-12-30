import requests
from sqlalchemy.orm import Session
from models import Weather
from datetime import datetime, timedelta


API_KEY = "06c83bce24b64dbeb17171411243012"
BASE_URL = "http://api.weatherapi.com/v1"

def fetch_weather(city: str):
    # Correct parameters for WeatherAPI
    params = {"key": API_KEY, "q": city, "aqi": "no"}  # 'key' is used for API Key, 'q' for city name
    response = requests.get(f"{BASE_URL}/current.json", params=params)  # Specify the endpoint for current weather

    if response.status_code == 200:
        data = response.json()
        return {
            "temperature": data["current"]["temp_c"],  # Access temperature in Celsius
            "description": data["current"]["condition"]["text"]  # Weather condition description
        }
    else:
        print(f"Error: {response.status_code}, {response.text}")  # Log error details for debugging
        return None


def save_weather(city: str, data: dict, db: Session):
    weather = Weather(
        city=city,
        temperature=data["temperature"],
        description=data["description"]

    )

    db.add(weather)
    db.commit()
    db.refresh(weather)
    return weather

def get_cached_weather(city: str, db: Session):
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    return db.query(Weather).filter(Weather.city == city, Weather.timestamp > one_hour_ago).first()
