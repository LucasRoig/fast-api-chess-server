from fastapi import APIRouter, UploadFile, File
from starlette.status import HTTP_200_OK

from app.models.schemas.pgn import PgnParseResponse
from app.services.chess import parse_pgn as do_parse_pgn

router = APIRouter()


@router.post("/parse", status_code=HTTP_200_OK, response_model=PgnParseResponse, name="pgn:parse")
async def parse_pgn(file: UploadFile = File(...)) -> PgnParseResponse:
    game = do_parse_pgn(await file.read())
    return PgnParseResponse(game=game)
