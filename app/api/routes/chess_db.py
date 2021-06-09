from fastapi import APIRouter, Depends, Body
from starlette.status import HTTP_201_CREATED

from app.api.dependencies.auth import requires_auth
from app.api.dependencies.database import get_repository
from app.db.repositories.chess_db import ChessDbRepository
from app.models.domain.chess_database import ChessDb
from app.models.domain.users import Auth0User
from app.models.schemas.chess_db import CreateDbRequest

router = APIRouter()

@router.post("/", status_code=HTTP_201_CREATED, response_model=ChessDb, name="db:create")
async def createDb(
    db_repo: ChessDbRepository = Depends(get_repository(ChessDbRepository)),
    db: CreateDbRequest = Body(..., embed=True),
    user: Auth0User = Depends(requires_auth)
) -> ChessDb:
    return await db_repo.create_db(name=db.name, user=user)
