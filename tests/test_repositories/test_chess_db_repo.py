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
