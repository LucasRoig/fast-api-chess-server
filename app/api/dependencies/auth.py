import json
from urllib.request import urlopen, Request

from jose import jwt
from loguru import logger
from fastapi import Header
from starlette.status import HTTP_401_UNAUTHORIZED

from app.api.errors.auth_error import AuthError
from app.core.config import AUTH0_DOMAIN, API_AUDIENCE, AUTH0_ALGORITHMS


def get_token_auth_header(authorization: str) -> str:
    if not authorization:
        raise AuthError("Authorization header is expected", HTTP_401_UNAUTHORIZED)
    parts = authorization.split()
    if len(parts) > 2 :
        raise AuthError("Authorization header must be Bearer token", HTTP_401_UNAUTHORIZED)
    if len(parts) < 2 :
        raise AuthError("Token not found", HTTP_401_UNAUTHORIZED)
    logger.info(parts[1])
    return parts[1]

def get_user(token: str) -> None:
    r = Request("https://"+AUTH0_DOMAIN+"/userinfo", headers={"Authorization": token})
    response = urlopen(r)
    j = json.loads(response.read())
    logger.info(j)

async def requires_auth(authorization: str= Header(None)) -> bool:
    token = get_token_auth_header(authorization)
    jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
    jwks = json.loads(jsonurl.read())
    try:
        unverified_header = jwt.get_unverified_header(token)
    except Exception:
        raise AuthError("unable to parse authentication token", HTTP_401_UNAUTHORIZED)
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
    if rsa_key:
        try:
            payload =  jwt.decode(
                token,
                rsa_key,
                algorithms=AUTH0_ALGORITHMS,
                audience=API_AUDIENCE,
                issuer="https://"+AUTH0_DOMAIN+"/"
            )
        except jwt.ExpiredSignatureError:
            raise AuthError("token is expired", HTTP_401_UNAUTHORIZED)
        except jwt.JWTClaimsError:
            raise AuthError("invalid claims", HTTP_401_UNAUTHORIZED)
        except Exception:
            raise AuthError("unable to parse authentication token", HTTP_401_UNAUTHORIZED)
        logger.info(payload)
        get_user(authorization)
        return True
    raise AuthError("Unable to find appropriate key", HTTP_401_UNAUTHORIZED)
