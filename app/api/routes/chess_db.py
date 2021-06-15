from typing import List

from fastapi import APIRouter, Depends, Body, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED

from app.api.dependencies.auth import requires_auth
from app.api.dependencies.database import get_repository
from app.db.repositories.chess_db import ChessDbRepository
from app.db.repositories.chess_db_game import ChessDbGameRepository
from app.models.domain.chess_database import ChessDb, ChessDbGame
from app.models.domain.users import Auth0User
from app.models.schemas.chess_db import CreateDbRequest, CreateDbGameRequest, DbDetailsResponse

router = APIRouter()


@router.post("/", status_code=HTTP_201_CREATED, response_model=ChessDb, name="db:create")
async def createDb(
        db_repo: ChessDbRepository = Depends(get_repository(ChessDbRepository)),
        db: CreateDbRequest = Body(..., embed=True),
        user: Auth0User = Depends(requires_auth)
) -> ChessDb:
    return await db_repo.create_db(name=db.name, user=user)


@router.get("/", status_code=HTTP_200_OK, response_model=List[ChessDb], name="db:get_all")
async def get_all_db(
        db_repo: ChessDbRepository = Depends(get_repository(ChessDbRepository)),
        user: Auth0User = Depends(requires_auth)
) -> List[ChessDb]:
    return await db_repo.get_db_for_user(user_id=user.id)


# @router.get("/{db_id}/games", status_code=HTTP_200_OK, response_model=List[ChessDbGame], name="db:get_games")
# async def get_games(
#         db_id: int,
#         db_repo: ChessDbRepository = Depends(get_repository(ChessDbRepository)),
#         db_game_repo: ChessDbGameRepository = Depends(get_repository(ChessDbGameRepository)),
#         user: Auth0User = Depends(requires_auth)
# ) -> List[ChessDbGame]:
#     db = await db_repo.find_by_id(db_id=db_id)
#     if not db:
#         raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="this database doesn't exists")
#     if db.user_id != user.id:
#         raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
#     games = await db_game_repo.find_by_db_id(db_id=db_id)
#     return games


@router.post("/{db_id}/games", status_code=HTTP_201_CREATED, response_model=ChessDbGame, name="db:create_game")
async def create_game(
        db_id: int,
        db_repo: ChessDbRepository = Depends(get_repository(ChessDbRepository)),
        db_game_repo: ChessDbGameRepository = Depends(get_repository(ChessDbGameRepository)),
        user: Auth0User = Depends(requires_auth),
        game: CreateDbGameRequest = Body(..., embed=True)
) -> ChessDbGame:
    db = await db_repo.find_by_id(db_id=db_id)
    if not db:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="this database doesn't exists")
    if db.user_id != user.id:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
    return await db_game_repo.create_game(db_id=db.id, user_id=user.id, white=game.white, black=game.black,
                                          event=game.event, date=game.date, result=game.result)


@router.get("/{db_id}", status_code=HTTP_200_OK, response_model=DbDetailsResponse, name="db:get_details")
async def get_db_details(
        db_id: int,
        db_repo: ChessDbRepository = Depends(get_repository(ChessDbRepository)),
        db_game_repo: ChessDbGameRepository = Depends(get_repository(ChessDbGameRepository)),
        user: Auth0User = Depends(requires_auth)
) -> DbDetailsResponse:
    db = await db_repo.find_by_id(db_id=db_id)
    if not db:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="this database doesn't exists")
    if db.user_id != user.id:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
    games = await db_game_repo.find_by_db_id(db_id=db_id)
    return DbDetailsResponse(
        database=db,
        games=games
    )


@router.delete("/{db_id}", status_code=HTTP_200_OK, response_model=None, name="db:delete_one")
async def delete_one(
        db_id: int,
        db_repo: ChessDbRepository = Depends(get_repository(ChessDbRepository)),
        user: Auth0User = Depends(requires_auth),
) -> None:
    db = await db_repo.find_by_id(db_id=db_id)
    if not db:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="this database doesn't exists")
    if db.user_id != user.id:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
    await db_repo.delete_db(db_id=db_id)
