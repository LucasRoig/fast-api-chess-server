from fastapi import APIRouter
from app.api.routes.authentication import router as auth
from app.api.routes.pgn import router as pgn

router = APIRouter()
router.include_router(auth, prefix="/auth", tags=["authentication"])
router.include_router(pgn, prefix="/pgn", tags=["pgn"])
