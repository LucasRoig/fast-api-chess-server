import pytest
from fastapi import FastAPI
from httpx import AsyncClient, Response
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from app.models.domain.users import UserInDB

pytestmark = pytest.mark.asyncio


async def post_login(client: AsyncClient, app: FastAPI, email: str, password: str) -> Response:
    json = {"user": {"email": email, "password": password}}
    return await client.post(app.url_path_for("auth:login"), json=json)


async def test_login_successful(client: AsyncClient, app: FastAPI, test_user: UserInDB) -> None:
    response = await post_login(client, app, test_user.email, "password")
    assert response.status_code == HTTP_200_OK


async def test_wrong_password(client: AsyncClient, app: FastAPI, test_user: UserInDB) -> None:
    response = await post_login(client, app, test_user.email, "wrong_password")
    assert response.status_code == HTTP_400_BAD_REQUEST


async def test_wrong_email(client: AsyncClient, app: FastAPI, test_user: UserInDB) -> None:
    response = await post_login(client, app, "wrong.email@test.com", "password")
    assert response.status_code == HTTP_400_BAD_REQUEST
