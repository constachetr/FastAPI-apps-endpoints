from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas, services

# Initialize database models
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app instance
app = FastAPI()

# Serve static files (CSS)
app.mount("/static", StaticFiles(directory="static"), name="static")


# Set up templates
templates = Jinja2Templates(directory="templates")

# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root endpoint for HTML interface
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Weather endpoint
@app.get("/weather/{city}", response_model=schemas.Weather_Response)
async def get_weather(city: str, db: Session = Depends(get_db)):
    # Check if cached weather data is available
    weather = services.get_cached_weather(city, db)
    if weather:
        return weather

    # Fetch fresh weather data
    weather_data = services.fetch_weather(city)
    if not weather_data:
        raise HTTPException(status_code=404, detail="City not found")

    # Save and return the new weather data
    return services.save_weather(city, weather_data, db)




