from app.models.schemas.rwschema import RWSchema


class CreateDbRequest(RWSchema):
    name: str
