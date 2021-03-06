from typing import List, Awaitable, Dict, Any


class Connection:
    def fetch(self, query: str, *args) -> Awaitable[List[Record]]: ...
    def fetchrow(self, query: str, *args) -> Awaitable[Record]: ...
    def __aenter__(self) -> Awaitable[Any]:...
    def __aexit__(self, exc_type, exc_val, exc_tb) -> Awaitable[Any]: ...

class Record(Dict[str,Any]):...
