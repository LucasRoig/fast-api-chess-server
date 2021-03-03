from app.models.domain.serializable_game import SerializableGame
from app.models.schemas.rwschema import RWSchema


class PgnParseResponse(RWSchema):
    game: SerializableGame
