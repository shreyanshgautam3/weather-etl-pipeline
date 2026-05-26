import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

# OpenWeatherMap configurations
API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = os.getenv("TARGET_CITY", "Lisbon")
URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

# Database Configurations
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

class WeatherData(BaseModel):
    city: str = Field(..., alias="name")
    temperature: float
    humidity: int
    timestamp: int
    country: str

    @field_validator("temperature")
    @classmethod
    def check_temperature_bounds(cls, v: float) -> float:
        if v < -50 or v > 60:
            raise ValueError("Temperature measurement anomaly.")
        return v
    

def fetch_weather() -> dict:
    if not API_KEY or "your_actual_api_key" in API_KEY:
        raise ValueError("Configure a valid OPENWEATHER_API_KEY in your .env file.")
    
    print(f"Fetching weather data for {CITY}...")
    response = requests.get(URL)
    response.raise_for_status()
    return response.json()


def transform_and_validate(raw_data: dict) -> WeatherData:
    flattened_data = {
        "name": raw_data.get("name"),
        "temperature": raw_data.get("main", {}).get("temp"),
        "humidity": raw_data.get("main", {}).get("humidity"),
        "timestamp": raw_data.get("dt"),
        "country": raw_data.get("sys", {}).get("country")
    }
    return WeatherData(**flattened_data)


def init_db(engine):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS weather_logs (
        id SERIAL PRIMARY KEY,
        city VARCHAR(100),
        temperature FLOAT,
        humidity INTEGER,
        timestamp BIGINT,
        country VARCHAR(10),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    with engine.begin() as conn:
        conn.execute(text(create_table_query))


def insert_weather_data(engine, record: WeatherData):
    cte_insert_query = """
    WITH new_weather AS (
        SELECT :city AS city,
               :temperature AS temperature,
               :humidity AS humidity,
               :timestamp AS timestamp,
               :country AS country
    )
    INSERT INTO weather_logs (city, temperature, humidity, timestamp, country)
    SELECT city, temperature, humidity, timestamp, country
    FROM new_weather
    WHERE NOT EXISTS (
        SELECT 1
        FROM weather_logs w
        WHERE w.city = new_weather.city AND w.timestamp = new_weather.timestamp
    );
    """
    with engine.begin() as conn:
        result = conn.execute(text(cte_insert_query), {
            "city": record.city,
            "temperature": record.temperature,
            "humidity": record.humidity,
            "timestamp": record.timestamp,
            "country": record.country
        })
        
        if result.rowcount > 0:
            print(f"[Database] Success: Logged data for {record.city}.")
        else:
            print(f"[Database] Skipped: Data for {record.city} at timestamp {record.timestamp} already exists.")


if __name__ == "__main__":
    try:
        # Step 1: Ingest & Validate
        api_response_dict = fetch_weather()
        cleaned_record = transform_and_validate(api_response_dict)

        print(f"Validated Data: {cleaned_record.city} | {cleaned_record.temperature}°C")
        
        # Step 2: Connect and process Database actions
        print("Establishing connection to PostgreSQL container...")
        engine = create_engine(DB_URL)

        init_db(engine)
        insert_weather_data(engine, cleaned_record)
        print(f"Pipeline complete for city: {cleaned_record.city} ({cleaned_record.country})")

    except Exception as e:
        print(f"\n[Pipeline error]: {e}")