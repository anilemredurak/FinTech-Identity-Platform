import pytest
import asyncio
from httpx import AsyncClient

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.api.deps import get_db
from app.db import models


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="module")
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    async_session = sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
def override_get_db(db_session):
    async def _override():
        yield db_session

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_full_auth_flow(override_get_db):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # register
        r = await ac.post("/auth/register", json={"email": "aed@example.com", "password": "secret123"})
        assert r.status_code == 201

        # login
        r = await ac.post("/auth/login", json={"email": "aed@example.com", "password": "secret123"})
        assert r.status_code == 200
        body = r.json()
        assert "access_token" in body
        assert "refresh_token" in body
        refresh = body["refresh_token"]

        # refresh
        r = await ac.post("/auth/refresh", json={"refresh_token": refresh})
        assert r.status_code == 200
        body = r.json()
        assert "access_token" in body

        # logout (revoke)
        r = await ac.post("/auth/logout", json={"refresh_token": refresh})
        assert r.status_code == 200
