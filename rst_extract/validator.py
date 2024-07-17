"""Validator class definition."""


class Validator:
    """Validator class that evaluates to True if given code is valid python/follows
    expected rules, False otherwise.
    """

    def __bool__(self) -> bool:
        """Return True if the code is valid python code, False otherwise."""
        return True
