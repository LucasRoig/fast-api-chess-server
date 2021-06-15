from typing import Optional, List
import datetime
from pydantic import Field

from app.models.domain.chess_database import ChessDb, ChessDbGame
from app.models.schemas.rwschema import RWSchema


class CreateDbRequest(RWSchema):
    name: str


class CreateDbGameRequest(RWSchema):
    white: str = Field(default="New Game")
    black: str = Field(default="")
    event: str = Field(default="")
    date: datetime.date = Field(default=datetime.date.today())
    result: str = Field(default="*")


class DbDetailsResponse(RWSchema):
    database: ChessDb
    games: List[ChessDbGame]
