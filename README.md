# OpenWeather Data Pipeline (Medallion Architecture)

A production-grade Data Engineering pipeline that extracts live weather data from the OpenWeatherMap API, validates it through data-quality checkpoints, and loads it into an idempotent PostgreSQL database. The entire system is containerized and orchestrated using Docker.



## System Architecture

This repository implements a **Medallion Architecture** to guarantee data quality and consistency as it moves through the system:

* **Bronze Layer (Raw Ingestion):** Fetches the immutable, raw JSON payload directly from the external REST API (`src/pipelines/bronze_ingest.py`).
* **Silver Layer (Cleaned & Validated):** Flattens the data and runs it through strict system type-hinting and data-integrity boundary checks using **Pydantic v2** (`src/schemas/silver_weather.py`).
* **Storage Layer (PostgreSQL):** Persists the validated data inside an isolated PostgreSQL 15 database container (`config/database.py`).
* **Idempotency (Deduplication):** Uses a **SQL Common Table Expression (CTE)** with a `WHERE NOT EXISTS` clause to ensure duplicate API payloads within the same time window are never written twice.

---

## Repository Structure

```
├── config/
│   └── database.py          # SQLAlchemy connection engine
├── src/
│   ├── pipelines/
│   │   └── bronze_ingest.py # Raw API ingestion engine
│   └── schemas/
│       └── silver_weather.py# Pydantic data validation quality rules
├── .env.example             # Template for required environment variables
├── .gitignore               # Prevents secrets/environments from tracking
├── docker-compose.yml       # Multi-container network and volume orchestration
├── Dockerfile               # Production image configuration for the Python app
├── main.py                  # Pipeline orchestrator (Entry point)
└── requirements.txt         # Project dependencies
```

## **Setup**
1. **Prerequisites**

Ensure you have the following installed on your machine:

* Docker Desktop
* Git

2. **Clone the Repository**

git clone https://github.com/[YOUR_GITHUB_USERNAME]/[YOUR_REPO_NAME].git

cd YOUR_REPO_NAME

3. **Configure Environment Variables**

Create a .env file in the root directory and add your credentials:

OPENWEATHER_API_KEY=your_actual_api_key_here

TARGET_CITY=Lisbon

DB_USER=postgres

DB_PASSWORD=password

DB_NAME=weather_db

DB_HOST=db

DB_PORT=5432

4. **Build and Run with Docker**

Spin up the fully orchestrated database network and app container with:

docker compose up --build

5. **Verify the Stored Data**

To check the validated data directly inside your running containerized database, run:

docker exec -it weather_postgres psql -U postgres -d weather_db -c "SELECT * FROM weather_logs;"
