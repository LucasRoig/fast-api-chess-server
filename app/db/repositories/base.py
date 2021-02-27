from typing import Any, List, Tuple, Union

from asyncpg.connection import Connection
from asyncpg import Record
from loguru import logger


def _log_query(query: str, query_params: Tuple[Union[str, int], ...]) -> None:
    logger.debug("query: {0}, values: {1}", query, query_params)


class BaseRepository:
    def __init__(self, conn: Connection) -> None:
        self._conn = conn

    @property
    def connection(self) -> Connection:
        return self._conn

    async def _log_and_fetch(self, query: str, *query_params: Union[str, int]) -> List[Record]:
        _log_query(query, query_params)
        return await self._conn.fetch(query, *query_params)

    async def _log_and_fetch_row(self, query: str, *query_params: Union[str, int]) -> Record:
        _log_query(query, query_params)
        return await self._conn.fetchrow(query, *query_params)
