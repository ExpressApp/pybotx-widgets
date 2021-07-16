"""Singleton for `undefined` value."""
from functools import lru_cache


class Undefined:
    @lru_cache()
    def __new__(cls) -> "Undefined":
        return super().__new__(cls)


undefined = Undefined()
