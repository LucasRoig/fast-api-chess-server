from typing import Awaitable

from .pool import Pool
from .connection import Record as Record

def create_pool(url: str, min_size:int = 10, max_size:int = 10) -> Awaitable[Pool]: ...
