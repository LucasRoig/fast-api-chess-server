from httpx import AsyncClient
from fastapi import FastAPI
import pytest
from starlette.status import HTTP_201_CREATED

from app.models.domain.users import Auth0User

pytestmark = pytest.mark.asyncio

async def test_create_db(authorized_client: AsyncClient, app: FastAPI, test_auth0_user: Auth0User):
    json = {
        "db": {
            "name": "db1"
        }
    }
    res = await authorized_client.post(app.url_path_for("db:create"), json=json)
    assert res.status_code == HTTP_201_CREATED
    print(res.json())
    assert res.json()["name"] == json["db"]["name"]
    assert res.json()["userId"] == test_auth0_user.id
