from app.models.domain.rwmodel import RWModel
import datetime


class ChessDb(RWModel):
    name: str
    id: int
    user_id: int


class ChessDbGame(RWModel):
    id: int
    chess_db_id: int
    user_id: int
    white: str
    black: str
    event: str
    date: datetime.date
    result: str
