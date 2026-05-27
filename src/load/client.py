import os
from sqlalchemy import create_engine, text
from src.transform.schemas import WeatherData
from dotenv import load_dotenv

load_dotenv()

def get_db_engine():
    # Constructs and returns the database connection engine
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")
    
    db_url = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    return create_engine(db_url)

def init_db(engine):
    # Initializes the weather logs table
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
            print(f"[Silver Database] Success: Logged validated data for {record.city}.")
        else:
            print(f"[Silver Database] Skipped: Duplicate record for {record.city} at timestamp {record.timestamp}.")