from sqlalchemy import text

def init_gold_db(engine):
    """Initializes the Gold layer analytics summary table."""
    create_gold_table = """
    CREATE TABLE IF NOT EXISTS gold_weather_summary (
        city VARCHAR(100),
        date DATE,
        avg_temperature FLOAT,
        max_temperature FLOAT,
        min_temperature FLOAT,
        reading_count INTEGER,
        PRIMARY KEY (city, date)
    );
    """
    with engine.begin() as conn:
        conn.execute(text(create_gold_table))

def generate_gold_insights(engine):
    """
    GOLD LAYER AGGREGATION:
    Reads clean data from the Silver table (weather_logs), computes daily 
    aggregates, and upserts them into the Gold business-intelligence layer.
    """
    gold_upsert_query = """
    WITH aggregated_metrics AS (
        SELECT 
            city,
            -- Convert Unix timestamp (BIGINT) back to a standard DATE format
            TO_TIMESTAMP(timestamp)::DATE as log_date,
            ROUND(AVG(temperature)::numeric, 2) as avg_temp,
            MAX(temperature) as max_temp,
            MIN(temperature) as min_temp,
            COUNT(*) as readings
        FROM weather_logs
        GROUP BY city, TO_TIMESTAMP(timestamp)::DATE
    )
    INSERT INTO gold_weather_summary (city, date, avg_temperature, max_temperature, min_temperature, reading_count)
    SELECT city, log_date, avg_temp, max_temp, min_temp, readings
    FROM aggregated_metrics
    ON CONFLICT (city, date) 
    DO UPDATE SET 
        avg_temperature = EXCLUDED.avg_temperature,
        max_temperature = EXCLUDED.max_temperature,
        min_temperature = EXCLUDED.min_temperature,
        reading_count = EXCLUDED.reading_count;
    """
    with engine.begin() as conn:
        result = conn.execute(text(gold_upsert_query))
        print(f"[Gold Database] Success: Analytics views updated / materialized.")