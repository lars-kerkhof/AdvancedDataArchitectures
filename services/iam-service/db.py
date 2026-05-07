import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy_utils import database_exists, create_database

# The database URL is provided as an env. variable
if 'DB_URL' in os.environ:
    db_url = os.environ['DB_URL']
else:
    db_url = 'sqlite:///user.db'

engine = create_engine(db_url)

# sqlalchemy_utils doesn't support BigQuery — skip database existence check.
# BigQuery datasets are managed externally via `bq mk`.
if not db_url.startswith('bigquery://'):
    if not database_exists(engine.url):
        create_database(engine.url)
    print(database_exists(engine.url))

Session = sessionmaker(bind=engine)
Base = declarative_base()
