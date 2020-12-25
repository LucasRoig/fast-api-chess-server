from fastapi import APIRouter
from app.api.routes.authentication import router as auth

router = APIRouter()
router.include_router(auth, prefix="/auth", tags=["authentication"])
