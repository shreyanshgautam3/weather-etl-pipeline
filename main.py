from dotenv import load_dotenv
from src.extract.weather_api import fetch_weather
from src.transform.schemas import transform_and_validate
from src.load.client import get_db_engine, init_db, insert_weather_data
from src.pipeline.analytics import init_gold_db, generate_gold_insights

def run_pipeline():
    
    # Load configuration
    load_dotenv()
    engine = get_db_engine()

    try:
        # 1. BRONZE LAYER: Raw Extraction
        raw_api_payload = fetch_weather()
        
        # 2. SILVER LAYER: Validation & Indempotent Storage
        cleaned_record = transform_and_validate(raw_api_payload)
        print(f"[Silver] Validated Schema: {cleaned_record.city} | {cleaned_record.temperature}°C")
        
        # Initialize Silver DB Table & Insert Clean Data
        init_db(engine)
        insert_weather_data(engine, cleaned_record)
        
        # 3. GOLD LAYER: Aggregation & Insights
        init_gold_db(engine)
        generate_gold_insights(engine)
        
        print(f"Pipeline ran successfully for {cleaned_record.city}!")

    except Exception as e:
        print(f"\n[Critical Pipeline Failure]: {e}")

if __name__ == "__main__":
    run_pipeline()