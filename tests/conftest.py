import pytest
import alembic.config
import app.api.dependencies.auth as auth
from os import environ

from asyncpg.pool import Pool
from fastapi import FastAPI
from starlette.config import Config
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from app.db.repositories.auth0_users import Auth0UsersRepository
from app.db.repositories.users import UsersRepository
from app.models.domain.users import UserInDB, Auth0User
from app.services import jwt

config = Config(".env")
TEST_DB_CONNECTION = config.get("TEST_DB_CONNECTION", cast=str)


@pytest.fixture
async def setup_test_db() -> None:
    environ["DB_CONNECTION"] = TEST_DB_CONNECTION


@pytest.fixture(autouse=True)
async def apply_migrations(setup_test_db: None) -> None:
    alembic.config.main(argv=["upgrade", "head"])
    yield
    alembic.config.main(argv=["downgrade", "base"])


@pytest.fixture
def app(apply_migrations: None) -> FastAPI:
    from app.main import get_application  # local import for testing purpose

    return get_application()


@pytest.fixture
async def initialized_app(app: FastAPI) -> FastAPI:
    async with LifespanManager(app):
        yield app


@pytest.fixture
def pool(initialized_app: FastAPI) -> Pool:
    return initialized_app.state.pool


@pytest.fixture
async def client(initialized_app: FastAPI) -> AsyncClient:
    async with AsyncClient(
            app=initialized_app,
            base_url="http://testserver",
            headers={"Content-Type": "application/json"},
    ) as client:
        yield client


@pytest.fixture
def authorization_prefix() -> str:
    from app.core.config import JWT_TOKEN_PREFIX

    return JWT_TOKEN_PREFIX


@pytest.fixture
async def test_user(pool: Pool) -> UserInDB:
    async with pool.acquire() as conn:
        return await UsersRepository(conn).create_user(
            email="test@test.com", password="password", username="username"
        )

test_user_sub = "default_test_user_sub"

@pytest.fixture
async def test_auth0_user(pool: Pool) -> Auth0User:
    sub = test_user_sub
    async with pool.acquire() as conn:
        return await Auth0UsersRepository(conn).get_or_create_by_sub(sub=sub)

@pytest.fixture
def token(test_user: UserInDB) -> str:
    from app.core.config import SECRET_KEY
    return jwt.create_access_token_for_user(test_user, SECRET_KEY)



@pytest.fixture
def authorized_client(
        client: AsyncClient, token: str, authorization_prefix: str, monkeypatch
) -> AsyncClient:
    async def return_test_user_sub(authorization: str) -> str:
        return authorization
    monkeypatch.setattr(auth, "get_sub", return_test_user_sub)
    client.headers = {
        "Authorization": f"{test_user_sub}",
        **client.headers,
    }
    return client
