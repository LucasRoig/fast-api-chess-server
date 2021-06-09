from app.db.repositories.base import BaseRepository
from loguru import logger

from app.models.domain.users import Auth0User

INSERT_OR_CREATE_BY_SUB = """
WITH e AS (INSERT INTO auth0_users (sub)
VALUES ($1)
ON CONFLICT DO NOTHING
RETURNING *)
SELECT * from e UNION (select * from auth0_users where sub=$1)
"""

class Auth0UsersRepository(BaseRepository):
    async def get_or_create_by_sub(self, *, sub: str) -> Auth0User:
        row = await self._log_and_fetch_row(INSERT_OR_CREATE_BY_SUB, sub)
        return Auth0User(
            id=row['id'],
            sub=row['sub']
        )

