from typing import List

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware

from app.api.errors.auth_error import AuthError, auth_error_handler
from app.api.errors.http_error import http_error_handler
from app.api.errors.validation_error import http422_error_handler
from app.core.config import ALLOWED_HOSTS, API_PREFIX
from app.core.events import create_start_app_handler, create_stop_app_handler
from app.api.routes.api import router as api_router

def get_application() -> FastAPI:
    application = FastAPI()
    allowed: List[str] = ["*"]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_HOSTS or allowed,
        allow_credentials=True,
        allow_methods=allowed,
        allow_headers=allowed)

    application.add_event_handler("startup", create_start_app_handler(application))
    application.add_event_handler("shutdown", create_stop_app_handler(application))

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, http422_error_handler)
    application.add_exception_handler(AuthError, auth_error_handler)

    application.include_router(api_router, prefix=API_PREFIX)

    return application


app = get_application()
