# db.py
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "extended-optics-495508-r1")
BQ_DATASET = os.getenv("BQ_DATASET", "enrollment_db")

DB_URL = os.getenv("DB_URL", f"bigquery://{GCP_PROJECT_ID}/{BQ_DATASET}")

engine = create_engine(
    DB_URL,
    location=os.getenv("BQ_LOCATION", "us-central1"),
)

Session = sessionmaker(bind=engine)
Base = declarative_base()
