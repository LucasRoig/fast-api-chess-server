from app.db.repositories.base import BaseRepository
from app.models.domain.chess_database import ChessDb
from app.models.domain.users import Auth0User

CREATE_DB = """
INSERT INTO chess_db (name, user_id) 
VALUES ($1, $2) 
RETURNING id, name, user_id
"""

class ChessDbRepository(BaseRepository):
    async def create_db(self, *, name: str, user: Auth0User) -> ChessDb:
        row = await self._log_and_fetch_row(CREATE_DB, name, user.id)
        return ChessDb(
            name=row["name"],
            id=row["id"],
            user_id=row["user_id"],
        )
