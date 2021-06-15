from typing import Any

from httpx import AsyncClient
from fastapi import FastAPI
import pytest
from requests import Response
from starlette.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED
from asyncpg.pool import Pool
import datetime

from app.db.repositories.chess_db_game import ChessDbGameRepository
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


async def test_get_db_games(authorized_client: AsyncClient, app: FastAPI, test_auth0_user: Auth0User, pool: Pool):
    db_name = "db1"
    db_id = (await post_create_db(authorized_client, app, db_name)).json()["id"]
    res = await authorized_client.get(app.url_path_for("db:get_details", db_id=db_id))
    assert res.status_code == HTTP_200_OK
    assert len(res.json()["games"]) == 0

    white = "a player"
    black = "another player"
    event = "London Classic"
    date = datetime.date(2018, 6, 12)
    result = "0-1"
    async with pool.acquire() as connection:
        game_repo = ChessDbGameRepository(connection)
        await game_repo.create_game(db_id=db_id, user_id=test_auth0_user.id, white=white, black=black, event=event,
                                    date=date, result=result)
    res = await authorized_client.get(app.url_path_for("db:get_details", db_id=db_id))
    assert res.status_code == HTTP_200_OK
    assert res.json()["database"]["name"] == db_name
    assert res.json()["database"]["id"] == db_id
    assert res.json()["database"]["userId"] == test_auth0_user.id

    assert len(res.json()["games"]) == 1
    g = res.json()["games"][0]
    assert g["white"] == white
    assert g["black"] == black
    assert g["event"] == event
    assert g["date"] == date.strftime("%Y-%m-%d")
    assert g["result"] == result
    assert g["chessDbId"] == db_id
    assert g["userId"] == test_auth0_user.id


async def test_cannot_get_games_if_not_owner(authorized_client: AsyncClient, app: FastAPI):
    db_id = (await post_create_db(authorized_client, app, "db1")).json()["id"]
    res = await authorized_client.get(app.url_path_for("db:get_details", db_id=db_id), headers={
        **authorized_client.headers,
        "Authorization": "another_user_sub",
    })
    assert res.status_code == HTTP_401_UNAUTHORIZED


async def test_get_games_returns_404_if_no_db(authorized_client: AsyncClient, app: FastAPI):
    res = await authorized_client.get(app.url_path_for("db:get_details", db_id="1"))
    assert res.status_code == HTTP_404_NOT_FOUND


async def test_create_db_game(authorized_client: AsyncClient, app: FastAPI, test_auth0_user: Auth0User, pool: Pool):
    db_id = (await post_create_db(authorized_client, app, "db1")).json()["id"]
    json = {
        "game": {
            "white": "a player",
            "black": "another player",
            "event": "London Classic",
            "date": datetime.date(2018, 6, 12).strftime("%Y-%m-%d"),
            "result": "0-1"
        }
    }
    res = await authorized_client.post(app.url_path_for("db:create_game", db_id=db_id), json=json)
    assert res.status_code == HTTP_201_CREATED
    g = res.json()
    assert g["white"] == json["game"]["white"]
    assert g["black"] == json["game"]["black"]
    assert g["event"] == json["game"]["event"]
    assert g["date"] == json["game"]["date"]
    assert g["result"] == json["game"]["result"]
    assert g["userId"] == test_auth0_user.id
    assert g["chessDbId"] == db_id
    assert g["id"] >= 0
    async with pool.acquire() as connection:
        repository = ChessDbGameRepository(connection)
        assert len(await repository.find_by_db_id(db_id=db_id)) == 1


async def test_create_game_returns_404_if_no_db(authorized_client: AsyncClient, app: FastAPI):
    json = {
        "game": {
            "white": "a player",
            "black": "another player",
            "event": "London Classic",
            "date": datetime.date(2018, 6, 12).strftime("%Y-%m-%d"),
            "result": "0-1"
        }
    }
    res = await authorized_client.post(app.url_path_for("db:create_game", db_id="1"), json=json)
    assert res.status_code == HTTP_404_NOT_FOUND


async def test_cannot_create_game_if_not_db_owner(authorized_client: AsyncClient, app: FastAPI):
    db_id = (await post_create_db(authorized_client, app, "db1")).json()["id"]
    json = {
        "game": {
            "white": "a player",
            "black": "another player",
            "event": "London Classic",
            "date": datetime.date(2018, 6, 12).strftime("%Y-%m-%d"),
            "result": "0-1"
        }
    }
    res = await authorized_client.post(app.url_path_for("db:create_game", db_id=db_id), json=json, headers={
        **authorized_client.headers,
        "Authorization": "another_user_sub",
    })
    assert res.status_code == HTTP_401_UNAUTHORIZED
