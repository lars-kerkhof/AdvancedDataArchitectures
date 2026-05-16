# db.py
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "extended-optics-495508-r1")
BQ_DATASET = os.getenv("BQ_DATASET", "enrollment_db")
BQ_LOCATION = os.getenv("BQ_LOCATION", "us-central1")

env_url = os.getenv("DB_URL")
if env_url and env_url.startswith("bigquery://"):
    DB_URL = env_url
else:
    DB_URL = f"bigquery://{GCP_PROJECT_ID}/{BQ_DATASET}"

engine = create_engine(
    DB_URL,
    connect_args={"location": BQ_LOCATION},
)

Session = sessionmaker(bind=engine)
Base = declarative_base()
