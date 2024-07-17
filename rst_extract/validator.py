"""Validator class definition."""

import logging
from ast import parse

from pydantic import BaseModel, StrictStr


class Validator(BaseModel):
    """Validator class that evaluates to True if given code is valid python/follows
    expected rules, False otherwise.
    """

    code: StrictStr = ''
    _exception: SyntaxError | None = None

    def __bool__(self) -> bool:
        """Return True if the code is valid python code, False otherwise."""
        return self.is_valid_python(self.code)

    @staticmethod
    def is_valid_python(code: str) -> bool:
        """Return True if the code is valid python code, False otherwise."""
        try:
            _ = parse(code, type_comments=True)
            return True

        except SyntaxError as err:
            _exception = err
            logging.info(
                'Got a syntax error while parsing code: %s("%s").',
                err.__class__.__name__,
                err.msg,
            )
            return False
