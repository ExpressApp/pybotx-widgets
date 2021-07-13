"""Singleton for `undefined` value."""


class Undefined:
    def __new__(cls) -> "Undefined":
        if not hasattr(cls, "instance"):  # noqa: WPS421
            cls.instance = super().__new__(cls)

        return cls.instance


undefined = Undefined()
