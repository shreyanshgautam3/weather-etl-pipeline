import os
import requests
from typing import Dict, Any

def fetch_weather() -> Dict[str, Any]:
    """ 
    BRONZE LAYER EXTRACTION:
    Fetches raw, unaltered JSON payload directly from the OpenWeatherMap API.
"""

    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    CITY = os.getenv("TARGET_CITY", "Lisbon")
    
    if not API_KEY or "your_actual_api_key" in API_KEY:
        raise ValueError("Configure a valid OPENWEATHER_API_KEY in your .env file.")
    
    # Constructing URL safely per-execution
    url = f"https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": CITY,
        "appid": API_KEY,
        "units": "metric"
    }
    
    print(f"[Bronze] Fetching raw weather data for {CITY}...")
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    
    raw_payload = response.json()
    
    return raw_payload