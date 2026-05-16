# db.py
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "extended-optics-495508-r1")
BQ_DATASET = os.getenv("BQ_DATASET", "enrollment_db")
BQ_LOCATION = os.getenv("BQ_LOCATION", "us-central1")

# FORCE BIGQUERY: If the environment variable is missing or hijacked by an SQLite default,
# explicitly construct the correct BigQuery string.
env_url = os.getenv("DB_URL")
if env_url and env_url.startswith("bigquery://"):
    DB_URL = env_url
else:
    DB_URL = f"bigquery://{GCP_PROJECT_ID}/{BQ_DATASET}"

# Standard practice: pass dialect-specific configurations via connect_args
engine = create_engine(
    DB_URL,
    connect_args={"location": BQ_LOCATION},
)

Session = sessionmaker(bind=engine)
Base = declarative_base()
