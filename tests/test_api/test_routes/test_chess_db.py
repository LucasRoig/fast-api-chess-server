from typing import Any

from httpx import AsyncClient
from fastapi import FastAPI
import pytest
from requests import Response
from starlette.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED

from app.models.domain.users import Auth0User

pytestmark = pytest.mark.asyncio

async def post_create_db(client: AsyncClient, app: FastAPI, db_name: str) -> Response:
    json = {
        "db": {
            "name": db_name
        }
    }
    return await client.post(app.url_path_for("db:create"), json=json)


async def test_create_db(authorized_client: AsyncClient, app: FastAPI, test_auth0_user: Auth0User):
    db_name = "db1"
    res = await post_create_db(authorized_client, app, db_name=db_name)
    assert res.status_code == HTTP_201_CREATED
    print(res.json())
    assert res.json()["name"] == db_name
    assert res.json()["userId"] == test_auth0_user.id

async def test_get_db(authorized_client: AsyncClient, app: FastAPI, test_auth0_user: Auth0User):
    db1 = "db1"
    db2 = "db2"
    await post_create_db(authorized_client, app, db1)
    await post_create_db(authorized_client, app, db2)
    res = await authorized_client.get(app.url_path_for("db:get_all"))
    assert res.status_code == HTTP_200_OK
    assert len(res.json()) == 2
    assert res.json()[0]["name"] == db1
    assert res.json()[0]["userId"] == test_auth0_user.id
    assert res.json()[0]["id"] > 0
    assert res.json()[1]["name"] == db2
    assert res.json()[1]["userId"] == test_auth0_user.id
    assert res.json()[1]["id"] > 0 and res.json()[1]["id"] != res.json()[0]["id"]

async def test_get_all_does_not_returns_another_user_db(authorized_client: AsyncClient, app: FastAPI):
    # post as user_1
    await post_create_db(authorized_client, app, "db1")
    # get as another user
    res = await authorized_client.get(app.url_path_for("db:get_all"), headers={
        **authorized_client.headers,
        "Authorization": "another_user_sub",
    })
    assert len(res.json()) == 0

async def test_delete_not_existing_db(authorized_client: AsyncClient, app: FastAPI):
    res = await authorized_client.delete(app.url_path_for("db:delete_one", db_id="1"))
    print(res.json())
    assert res.status_code == HTTP_404_NOT_FOUND

async def test_cannot_delete_another_user_db(authorized_client: AsyncClient, app: FastAPI):
    # post as user_1
    res = await post_create_db(authorized_client, app, "db1")
    id = res.json()["id"]
    # delete as another user
    res = await authorized_client.delete(app.url_path_for("db:delete_one", db_id=id), headers={
        **authorized_client.headers,
        "Authorization": "another_user_sub",
    })
    assert res.status_code == HTTP_401_UNAUTHORIZED
    # fetch as user 1
    res = await authorized_client.get(app.url_path_for("db:get_all"))
    assert res.status_code == HTTP_200_OK
    assert len(res.json()) == 1

async def test_delete_db(authorized_client: AsyncClient, app: FastAPI):
    await post_create_db(authorized_client, app, "db1")
    res = await authorized_client.get(app.url_path_for("db:get_all"))
    assert res.status_code == HTTP_200_OK
    assert len(res.json()) == 1
    db_id = res.json()[0]["id"]

    res = await authorized_client.delete(app.url_path_for("db:delete_one", db_id=db_id))
    assert res.status_code == HTTP_200_OK

    res = await authorized_client.get(app.url_path_for("db:get_all"))
    assert res.status_code == HTTP_200_OK
    assert len(res.json()) == 0
