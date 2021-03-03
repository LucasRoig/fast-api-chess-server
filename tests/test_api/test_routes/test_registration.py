import pytest
from asyncpg.pool import Pool
from fastapi import FastAPI
from httpx import AsyncClient
from starlette.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST

from app.db.repositories.users import UsersRepository
from app.models.domain.users import UserInDB

pytestmark = pytest.mark.asyncio


async def post_user(email: str, username: str, password: str, app: FastAPI, client: AsyncClient):
    json = {
        "user": {"email": email, "username": username, "password": password}
    }
    return await client.post(app.url_path_for("auth:register"), json=json)


async def test_user_success_registration(client: AsyncClient, app: FastAPI, pool: Pool):
    email, username, password = "test@test.com", "user", "password"
    response = await post_user(email, username, password, app, client)
    assert response.status_code == HTTP_400_BAD_REQUEST

    async with pool.acquire() as connection:
        repo = UsersRepository(connection)
        user = await repo.get_user_by_email(email=email)
        assert user.email == email
        assert user.username == username
        assert user.check_password(password)


async def test_failed_user_registration_when_email_is_taken(client: AsyncClient, app: FastAPI, test_user: UserInDB):
    email, username, password = test_user.email, "user_not_taken", "password"
    response = await post_user(email, username, password, app, client)
    assert response.status_code == HTTP_400_BAD_REQUEST


async def test_failed_user_registration_when_username_is_taken(client: AsyncClient, app: FastAPI, test_user: UserInDB):
    email, username, password = "email.not.taken@test.com", test_user.username, "password"
    response = await post_user(email, username, password, app, client)
    assert response.status_code == HTTP_400_BAD_REQUEST
