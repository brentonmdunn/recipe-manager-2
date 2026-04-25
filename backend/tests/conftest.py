import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_session
from app.main import app
from app.models import Base

TEST_DATABASE_URL = "sqlite+aiosqlite://"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_session():
    async with TestSession() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    await client.post(
        "/api/v1/auth/register",
        json={"username": "admin", "password": "testpassword123"},
    )
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "testpassword123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
