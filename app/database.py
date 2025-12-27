from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# Create database engine
# Replace postgresql:// with postgresql+psycopg:// for psycopg3
database_url = settings.database_url.replace("postgresql://", "postgresql+psycopg://")
engine = create_engine(
    database_url,
    pool_pre_ping=True,
    echo=False,  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
