from typing import List

from asyncpg import Record

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
        return parse_record(record=row)

    async def delete_db(self, *, db_id: int) -> bool:
        delete_db = """
        DELETE FROM chess_db WHERE id = $1
        """
        await self._log_and_fetch_row(delete_db, db_id)
        return True

    async def get_db_for_user(self, *, user_id: int) -> List[ChessDb]:
        find_db = """
        SELECT * FROM chess_db WHERE user_id = $1
        """
        rows = await self._log_and_fetch(find_db, user_id)
        return [
            parse_record(record=record)
            for record in rows
        ]

def parse_record(*, record: Record) -> ChessDb:
    return ChessDb(
        name=record["name"],
        id=record["id"],
        user_id=record["user_id"],
    )
