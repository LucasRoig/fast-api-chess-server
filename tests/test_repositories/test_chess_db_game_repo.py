import datetime
import pytest
from asyncpg.pool import Pool

from app.db.repositories.chess_db import ChessDbRepository
from app.db.repositories.chess_db_game import ChessDbGameRepository
from app.models.domain.chess_database import ChessDbGame
from app.models.domain.users import Auth0User

pytestmark = pytest.mark.asyncio


async def test_create_game(pool: Pool, test_auth0_user: Auth0User):
    async with pool.acquire() as conn:
        db_repo = ChessDbRepository(conn)
        game_repo = ChessDbGameRepository(conn)
        db = await db_repo.create_db(name="db1", user=test_auth0_user)
        expected = ChessDbGame(
            date=datetime.date(1999, 1, 1),
            result="1-0",
            event="Some Tournament",
            black="Some guy",
            white="another dude",
            chess_db_id=db.id,
            user_id=test_auth0_user.id,
            id=11
        )
        actual = await game_repo.create_game(
            result=expected.result,
            date=expected.date,
            user_id=expected.user_id,
            white=expected.white,
            black=expected.black,
            event=expected.event,
            db_id=expected.chess_db_id
        )
        assert expected.result == actual.result
        assert expected.date == actual.date
        assert expected.user_id == actual.user_id
        assert expected.id >= 0
        assert expected.event == actual.event
        assert expected.white == actual.white
        assert expected.black == actual.black
        assert expected.chess_db_id == actual.chess_db_id

        # Test find by id
        assert actual == (await game_repo.find_by_id(actual.id))

        # Test find by db id
        by_db_id = await game_repo.find_by_db_id(db_id=db.id)
        assert len(by_db_id) == 1
        assert actual == by_db_id[0]


async def test_update_game(pool: Pool, test_auth0_user: Auth0User):
    async with pool.acquire() as conn:
        db_repo = ChessDbRepository(conn)
        game_repo = ChessDbGameRepository(conn)
        db = await db_repo.create_db(name="db1", user=test_auth0_user)
        expected = ChessDbGame(
            date=datetime.date(1999, 1, 1),
            result="1-0",
            event="Some Tournament",
            black="Some guy",
            white="another dude",
            chess_db_id=db.id,
            user_id=test_auth0_user.id,
            id=11
        )
        expected = await game_repo.create_game(db_id=expected.chess_db_id, user_id=expected.user_id,
                                               white=expected.white,
                                               black=expected.black, event=expected.event, date=expected.date,
                                               result=expected.result)
        expected.date = datetime.date(2000, 1, 2)
        expected.result = "*"
        expected.event = "Madrid"
        expected.black = "A player"
        expected.white = "another player"
        actual = await game_repo.update_game(game=expected)
        assert actual == expected
        assert len(await game_repo.find_by_db_id(db_id=db.id)) == 1


async def test_delete_game(pool: Pool, test_auth0_user: Auth0User):
    async with pool.acquire() as conn:
        db_repo = ChessDbRepository(conn)
        game_repo = ChessDbGameRepository(conn)
        db = await db_repo.create_db(name="db1", user=test_auth0_user)
        expected = ChessDbGame(
            date=datetime.date(1999, 1, 1),
            result="1-0",
            event="Some Tournament",
            black="Some guy",
            white="another dude",
            chess_db_id=db.id,
            user_id=test_auth0_user.id,
            id=11
        )
        g = await game_repo.create_game(db_id=expected.chess_db_id, user_id=expected.user_id, white=expected.white,
                                    black=expected.black, event=expected.event, date=expected.date,
                                    result=expected.result)
        assert len(await game_repo.find_by_db_id(db_id=db.id)) == 1
        await game_repo.delete_game(game_id=g.id)
        assert len(await game_repo.find_by_db_id(db_id=db.id)) == 0
