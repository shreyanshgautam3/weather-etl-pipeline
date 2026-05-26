import os
import requests
from typing import Dict, Any

def fetch_weather() -> Dict[str, Any]:
    """
    BRONZE LAYER EXTRACTION:
    Fetches raw, unaltered JSON payload directly from the OpenWeatherMap API.
    
    Returns:
        Dict[str, Any]: The raw, unmodified JSON dictionary from the endpoint.
    """
    # Fetch configurations dynamically within the function call scope
    api_key = os.getenv("OPENWEATHER_API_KEY")
    city = os.getenv("TARGET_CITY", "Lisbon")
    
    if not api_key or "your_actual_api_key" in api_key:
        raise ValueError("Configure a valid OPENWEATHER_API_KEY in your .env file.")
    
    # Constructing URL safely per-execution
    url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }
    
    print(f"[Bronze] Fetching raw weather data for {city}...")
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    
    raw_payload = response.json()
    
    return raw_payload