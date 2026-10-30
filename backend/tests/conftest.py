import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

import app.models  # noqa: F401  (registers all tables)
from app.core.config import settings
from app.db.session import Base, get_db
from app.main import app
from app.models import Category, Location

# Same server and login as the real database, but a different database name.
TEST_DB_NAME = "mealconnect_test"
engine = create_engine(make_url(settings.database_url).set(database=TEST_DB_NAME), pool_pre_ping=True)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    assert engine.url.database == TEST_DB_NAME  # safety: never run against the real database
    Base.metadata.create_all(engine)
    yield
    engine.dispose()


@pytest.fixture(autouse=True)
def clean_database():
    """Empty every table before each test, so tests never affect each other."""
    assert engine.url.database == TEST_DB_NAME
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE reservations, meals, locations, categories, users RESTART IDENTITY CASCADE"))
    yield


@pytest.fixture
def db():
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    def override_get_db():
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def base(db):
    """A category and a location that meals can point to."""
    category = Category(name="Lunch", description="Midday meals")
    location = Location(name="Green Leaf Cafe", address="12 MG Road", city="Bangalore")
    db.add_all([category, location])
    db.commit()
    return {"category_id": category.id, "location_id": location.id}