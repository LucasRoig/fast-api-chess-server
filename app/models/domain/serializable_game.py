from typing import Dict, List, Optional

from pydantic import Field

from app.models.domain.rwmodel import RWModel

class Move (RWModel):
    from_square: str = Field(alias="from")
    to: str
    promotion: Optional[str]

class SerializablePosition(RWModel):
    index: int
    next_position_index: Optional[int]
    variations_indexes: List[int]
    nags: List[int]
    fen: str
    comment: Optional[str]
    commentBefore: Optional[str]
    move: Move
    san: str
    is_mainline: bool

class SerializableGame(RWModel):
    headers: Dict[str, str]
    comment: str
    positions: List[SerializablePosition]
