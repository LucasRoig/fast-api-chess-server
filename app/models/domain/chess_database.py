from app.models.domain.rwmodel import RWModel


class ChessDb(RWModel):
    name: str
    id: int
    user_id: int
