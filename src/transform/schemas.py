from pydantic import BaseModel, Field, field_validator
from typing import Dict, Any

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

def transform_and_validate(raw_data: Dict[str, Any]) -> WeatherData:
    """
    SILVER LAYER TRANSFORMATION:
    Parses and flattens raw Bronze JSON payloads, matching them 
    against strict Pydantic schemas for data type safety.
    """
    flattened_data = {
        "name": raw_data.get("name"),
        "temperature": raw_data.get("main", {}).get("temp"),
        "humidity": raw_data.get("main", {}).get("humidity"),
        "timestamp": raw_data.get("dt"),
        "country": raw_data.get("sys", {}).get("country")
    }
    return WeatherData(**flattened_data)