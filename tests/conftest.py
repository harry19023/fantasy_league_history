"""Pytest configuration and fixtures."""

import importlib
import os
import time

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import app.config
import app.database
import app.models
from app.database import Base

# Set test database URL before importing app modules
_test_db_url = None


def get_test_db_url(database_url: str) -> str:
    """Get test database URL from main database URL."""
    base_url = database_url.rsplit("/", 1)[0]
    test_db_url = f"{base_url}/fantasy_league_test"
    return test_db_url.replace("postgresql://", "postgresql+psycopg://")


def create_test_database(
    database_url: str, test_db_name: str = "fantasy_league_test"
) -> str:
    """Create a test database in the same PostgreSQL server.

    Returns the test database URL.
    """
    # Parse the database URL to get connection info without the database name
    parts = database_url.rsplit("/", 1)
    server_url = f"{parts[0]}/postgres"
    server_url = server_url.replace("postgresql://", "postgresql+psycopg://")

    # Connect to PostgreSQL server (not a specific database)
    server_engine = create_engine(server_url, isolation_level="AUTOCOMMIT")

    # Create test database if it doesn't exist
    with server_engine.connect() as conn:
        result = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
            {"dbname": test_db_name},
        )
        exists = result.fetchone() is not None

        if not exists:
            conn.execute(text(f'CREATE DATABASE "{test_db_name}"'))
            print(f"Created test database: {test_db_name}")
        else:
            print(f"Test database already exists: {test_db_name}")

    server_engine.dispose()

    # Return the test database URL
    return get_test_db_url(database_url)


def wait_for_database(engine, max_attempts: int = 15, delay: int = 2):
    """Wait for database to be ready."""
    for i in range(max_attempts):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            if i == max_attempts - 1:
                return False
            time.sleep(delay)
    return False


def recreate_schema(engine):
    """Drop and recreate all tables in the database."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Wait for PostgreSQL, create test database, and initialize schema.

    This fixture runs once per test session and:
    1. Waits for PostgreSQL server to be ready (max 30 seconds)
    2. Creates a test database if it doesn't exist
    3. Sets DATABASE_URL to use the test database
    4. Drops and recreates all tables to match current models
    """
    global _test_db_url

    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        return

    # Wait for PostgreSQL server to be ready
    server_url = database_url.rsplit("/", 1)[0] + "/postgres"
    server_url = server_url.replace("postgresql://", "postgresql+psycopg://")
    server_engine = create_engine(server_url)

    if not wait_for_database(server_engine):
        print("Database not available, skipping initialization")
        server_engine.dispose()
        return

    server_engine.dispose()

    # Create test database
    test_db_url = create_test_database(database_url)
    _test_db_url = test_db_url

    # Override DATABASE_URL to use test database
    test_db_url_env = test_db_url.replace("postgresql+psycopg://", "postgresql://")
    os.environ["DATABASE_URL"] = test_db_url_env

    # Reload config and database modules to pick up new DATABASE_URL
    importlib.reload(app.config)
    importlib.reload(app.database)

    # Create engine for test database and recreate schema
    test_engine = create_engine(test_db_url, pool_pre_ping=True)

    if not wait_for_database(test_engine, max_attempts=5, delay=1):
        print("Test database not ready")
        test_engine.dispose()
        return

    try:
        recreate_schema(test_engine)
        print("Test database schema recreated successfully")
    except Exception as e:
        print(f"Database schema recreation error: {e}")

    test_engine.dispose()


@pytest.fixture(scope="function", autouse=True)
def ensure_db_schema():
    """Ensure database schema exists before each test.

    This fixture runs before each test and recreates the schema to ensure
    it matches the current models.
    """
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        return

    test_db_url = get_test_db_url(database_url)
    test_engine = create_engine(test_db_url, pool_pre_ping=True)

    try:
        recreate_schema(test_engine)
    except Exception as e:
        print(f"Warning: Could not recreate schema: {e}")
    finally:
        test_engine.dispose()


@pytest.fixture
def db_session():
    """Get database session for test database.

    This fixture provides a database session that uses the test database.
    Uncommitted changes are rolled back after each test.
    """
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        db = app.database.SessionLocal()
        try:
            yield db
        finally:
            db.close()
        return

    # Create engine and session for test database
    test_db_url = get_test_db_url(database_url)
    test_engine = create_engine(test_db_url, pool_pre_ping=True)
    test_session_local = sessionmaker(
        autocommit=False, autoflush=False, bind=test_engine
    )

    db = test_session_local()
    try:
        yield db
        db.rollback()
    finally:
        db.close()
        test_engine.dispose()
