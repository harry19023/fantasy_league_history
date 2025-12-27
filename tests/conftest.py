"""Pytest configuration and fixtures."""

import os
import time

import pytest
from sqlalchemy import create_engine, text

# Set test database URL before importing app modules
_test_db_url = None


def create_test_database(
    database_url: str, test_db_name: str = "fantasy_league_test"
) -> str:
    """Create a test database in the same PostgreSQL server.

    Returns the test database URL.
    """
    # Parse the database URL to get connection info without the database name
    # Format: postgresql://user:password@host:port/database
    if "postgresql://" in database_url:
        # Remove database name and connect to postgres database
        parts = database_url.rsplit("/", 1)
        server_url = f"{parts[0]}/postgres"
    else:
        # Already parsed or different format
        server_url = database_url.rsplit("/", 1)[0] + "/postgres"

    # Replace postgresql:// with postgresql+psycopg:// for psycopg3
    server_url = server_url.replace("postgresql://", "postgresql+psycopg://")

    # Connect to PostgreSQL server (not a specific database)
    server_engine = create_engine(server_url, isolation_level="AUTOCOMMIT")

    # Create test database if it doesn't exist
    with server_engine.connect() as conn:
        # Check if database exists
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
    test_db_url = database_url.rsplit("/", 1)[0] + f"/{test_db_name}"
    return test_db_url.replace("postgresql://", "postgresql+psycopg://")


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Wait for PostgreSQL, create test database, and initialize tables.

    This fixture will:
    1. Wait for PostgreSQL server to be ready (max 30 seconds)
    2. Create a test database if it doesn't exist
    3. Set DATABASE_URL to use the test database
    4. Initialize database tables in the test database
    5. Skip silently if database is not available (for tests that don't need it)
    """
    global _test_db_url

    # Only attempt database setup if DATABASE_URL is set
    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        # No database URL set, skip initialization
        return

    # Wait for PostgreSQL server to be ready (max 30 seconds)
    # Connect to postgres database to check server availability
    server_url = database_url.rsplit("/", 1)[0] + "/postgres"
    server_url = server_url.replace("postgresql://", "postgresql+psycopg://")
    server_engine = create_engine(server_url)

    for i in range(15):
        try:
            with server_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            break
        except Exception:
            if i == 14:
                # Database not available - this is okay for tests that don't need it
                print("Database not available, skipping initialization")
                server_engine.dispose()
                return
            time.sleep(2)

    server_engine.dispose()

    # Create test database
    test_db_url = create_test_database(database_url)
    _test_db_url = test_db_url

    # Override DATABASE_URL to use test database (before any imports)
    # This ensures app.database uses the test database
    test_db_url_env = test_db_url.replace("postgresql+psycopg://", "postgresql://")
    os.environ["DATABASE_URL"] = test_db_url_env

    # Create engine for test database
    test_engine = create_engine(test_db_url, pool_pre_ping=True)

    # Wait for test database to be ready
    for i in range(5):
        try:
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            break
        except Exception:
            if i == 4:
                print("Test database not ready")
                test_engine.dispose()
                return
            time.sleep(1)

    # Import Base and models after setting DATABASE_URL so they use the test database
    # Reimport app modules to use the new DATABASE_URL
    import importlib

    import app.config
    import app.database

    # Reload config and database modules to pick up new DATABASE_URL
    importlib.reload(app.config)
    importlib.reload(app.database)

    # Import models to register them with Base.metadata
    from app.database import Base
    from app.models import League, Matchup, Player, Roster, Team  # noqa: F401

    # Initialize database tables in test database using the test engine
    try:
        Base.metadata.create_all(bind=test_engine)
        print("Test database initialized successfully")
    except Exception as e:
        print(f"Database initialization note: {e}")

    test_engine.dispose()
