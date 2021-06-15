from app.db.repositories.base import BaseRepository
import datetime
from typing import List
from app.models.domain.chess_database import ChessDbGame
from asyncpg import Record


class ChessDbGameRepository(BaseRepository):
    async def find_by_id(self, id: int) -> ChessDbGame:
        query = """
        SELECT * FROM chess_db_games WHERE id = $1
        """
        row = await self._log_and_fetch_row(query, id)
        return parse_game_record(row)

    async def find_by_db_id(self, *, db_id: int) -> List[ChessDbGame]:
        query = """
        SELECT * FROM chess_db_games WHERE chess_db_id = $1
        """
        rows = await self._log_and_fetch(query, db_id)
        return [
            parse_game_record(row)
            for row in rows
        ]

    async def create_game(self, *, db_id: int, user_id: int, white: str = "New Game", black: str = "", event: str = "",
                          date: datetime.date = datetime.date.today(),
                          result: str = "*") -> ChessDbGame:
        query = """
        INSERT INTO chess_db_games (chess_db_id, user_id, white, black, event, date, result) 
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING *
        """
        row = await self._log_and_fetch_row(query, db_id, user_id, white, black, event, date, result)
        return parse_game_record(row)

    async def update_game(self, *, game: ChessDbGame) -> ChessDbGame:
        query = """
        UPDATE chess_db_games
        SET chess_db_id = $1,
        user_id = $2,
        white = $3,
        black = $4,
        event = $5,
        date = $6,
        result = $7
        WHERE id = $8
        RETURNING *
        """
        row = await self._log_and_fetch_row(query, game.chess_db_id, game.user_id, game.white, game.black, game.event,
                                            game.date, game.result, game.id)
        return parse_game_record(row)

    async def delete_game(self, *, game_id: int) -> None:
        query = """
        DELETE FROM chess_db_games WHERE id = $1
        """
        await self._log_and_fetch_row(query, game_id)


def parse_game_record(record: Record) -> ChessDbGame:
    return ChessDbGame(
        id=record["id"],
        chess_db_id=record["chess_db_id"],
        white=record["white"],
        black=record["black"],
        event=record["event"],
        result=record["result"],
        user_id=record["user_id"],
        date=record["date"]
    )
