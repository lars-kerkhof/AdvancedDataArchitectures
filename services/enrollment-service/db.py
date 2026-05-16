import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Read strictly from environment variables with safe fallbacks
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "extended-optics-495508-r1")
BQ_DATASET = os.getenv("BQ_DATASET", "enrollment_db")
BQ_LOCATION = os.getenv("BQ_LOCATION", "us-central1")

# Dynamically construct or read the DB URL, forcing the location query parameter
env_url = os.getenv("DB_URL")
if env_url:
    if "location=" not in env_url:
        separator = "&" if "?" in env_url else "?"
        DB_URL = f"{env_url}{separator}location={BQ_LOCATION}"
    else:
        DB_URL = env_url
else:
    DB_URL = f"bigquery://{GCP_PROJECT_ID}/{BQ_DATASET}?location={BQ_LOCATION}"

engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)
Base = declarative_base()
