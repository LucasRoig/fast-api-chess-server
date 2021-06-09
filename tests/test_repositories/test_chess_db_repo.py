import pytest
from asyncpg.pool import Pool

from app.db.repositories.chess_db import ChessDbRepository
from app.models.domain.users import Auth0User

pytestmark = pytest.mark.asyncio

async def test_create_db(pool: Pool, test_auth0_user: Auth0User):
    db_name = "testDb"
    async with pool.acquire() as connection:
        repo = ChessDbRepository(connection)
        db = await repo.create_db(name=db_name, user=test_auth0_user)
        assert db.name == db_name
        assert db.user_id == test_auth0_user.id
        assert db.id >= 0

async def test_get_db(pool: Pool, test_auth0_user: Auth0User):
    db1 = "db1"
    db2 = "db2"
    async with pool.acquire() as connection:
        repo = ChessDbRepository(connection)
        await repo.create_db(name=db1, user=test_auth0_user)
        await repo.create_db(name=db2, user=test_auth0_user)
        res = await repo.get_db_for_user(user_id=test_auth0_user.id)
        assert len(res) == 2
        assert res[0].name == db1
        assert res[0].user_id == test_auth0_user.id
        assert res[0].id > 0
        assert res[1].name == db2
        assert res[1].id > 0 and res[1].id != res[0].id
        assert res[1].user_id == test_auth0_user.id

async def test_delete_db(pool: Pool, test_auth0_user: Auth0User):
    async with pool.acquire() as connection:
        repo = ChessDbRepository(connection)
        res = await repo.create_db(name="test", user=test_auth0_user)
        assert len(await repo.get_db_for_user(user_id=test_auth0_user.id)) == 1
        res = await repo.delete_db(db_id=res.id)
        assert res == True
        assert len(await repo.get_db_for_user(user_id=test_auth0_user.id)) == 0
