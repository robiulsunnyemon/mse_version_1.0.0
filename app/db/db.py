import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


# Load .env
load_dotenv()


# Database configuration
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Create database URL
database_url = (
    f"postgresql://"
    f"{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


# Create engine
engine = create_engine(
    database_url,
    echo=True
)

# Create session
Session = sessionmaker(
    bind=engine
)

# Base model
Base = declarative_base()

# Database dependency
def get_db():
    db = Session()

    try:
        yield db
    finally:
        db.close()