from typing import Optional

from app.db.errors import EntityDoesNotExist
from app.db.repositories.base import BaseRepository
from app.models.domain.users import User, UserInDB

GET_USER_QUERY = """
SELECT u.id,
    u.username,
    u.email,
    u.salt,
    u.hashed_password,
    u.created_at,
    u.updated_at
FROM users u
"""

FILTER_USERNAME = """
WHERE u.username = $1
LIMIT 1
"""

FILTER_EMAIL = """
WHERE u.email = $1
LIMIT 1
"""

INSERT_USER_QUERY = """
INSERT INTO users (username, email, salt, hashed_password) 
VALUES ($1, $2, $3, $4) 
RETURNING id,
    username,
    email,
    salt,
    hashed_password,
    created_at,
    updated_at
"""

FIND_BY_USERNAME = "".join((GET_USER_QUERY, FILTER_USERNAME))
FIND_BY_EMAIL = "".join((GET_USER_QUERY, FILTER_EMAIL))


class UsersRepository(BaseRepository):
    async def get_user_by_email(self, *, email: str) -> UserInDB:
        user_row = await self._log_and_fetch_row(FIND_BY_EMAIL, email)
        if user_row:
            return UserInDB(**user_row)

        raise EntityDoesNotExist("user with email {0} does not exist".format(email))

    async def get_user_by_username(self, *, username: str) -> UserInDB:
        user_row = await self._log_and_fetch_row(FIND_BY_USERNAME, username)
        if user_row:
            return UserInDB(**user_row)

        raise EntityDoesNotExist("user with username {0} does not exist".format(username))

    async def create_user(self, *, username: str, email: str, password: str) -> UserInDB:
        user = UserInDB(username=username, email=email)
        user.change_password(password)
        user_row = await self._log_and_fetch_row(INSERT_USER_QUERY, user.username, user.email, user.salt,
                                                 user.hashed_password)

        return user.copy(update=dict(user_row))
