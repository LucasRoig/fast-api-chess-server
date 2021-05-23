from starlette.requests import Request
from starlette.responses import JSONResponse


class AuthError(Exception):
    def __init__(self, error: str, status_code: int):
        self.error = error
        self.status_code = status_code

async def auth_error_handler(
        _: Request,
        exc: AuthError,
) -> JSONResponse:
    return JSONResponse(
        {"errors": exc.error},
        status_code=exc.status_code,
    )
