"""Validator class definition."""

import ast
import builtins
import logging
from ast import parse

from pydantic import BaseModel, StrictStr


class _DefinedVariableAccountant(ast.NodeVisitor):
    defined_variables: set[StrictStr]
    undefined_variables: set[StrictStr]

    _builtins = set(dir(builtins))

    def __init__(self) -> None:
        self.defined_variables = set()
        self.undefined_variables = set()

    def visit_Assign(self, node: ast.Assign) -> None:  # noqa: N802
        """Visit Assign node and add defined variables to the defined_variables set.

        NOTE: This method must have the exact case here, as it is called by the
        ast.NodeVisitor.
        """
        logging.debug('Visiting Assign node: %s', node)

        for target in node.targets:
            if isinstance(target, ast.Name):
                logging.debug('Adding defined variable: %s', target.id)
                self.defined_variables.add(target.id)

        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:  # noqa: N802
        """Visit Name node and add undefined variables to the undefined_variables set.

        NOTE: This method must have the exact case here, as it is called by the
        ast.NodeVisitor.
        """
        logging.debug('Visiting Name node: %s', node)

        if node.id not in self.defined_variables | self._builtins:
            logging.debug('Adding undefined variable: %s', node.id)
            self.undefined_variables.add(node.id)

        self.generic_visit(node)


class Validator(BaseModel):
    """Validator class that evaluates to True if given code is valid python/follows
    expected rules, False otherwise.
    """

    code: StrictStr = ''

    def __bool__(self) -> bool:
        """Return True if the code is valid python code, False otherwise."""
        return self.is_valid_python(self.code)

    @staticmethod
    def is_valid_python(code: str) -> bool:
        """Return True if the code is valid python code, False otherwise."""
        try:
            ast_tree = parse(code, type_comments=True)

            # Check for undefined variables
            accountant = _DefinedVariableAccountant()
            accountant.visit(ast_tree)

            if accountant.undefined_variables:
                msg = (
                    'Undefined variables: ',
                    "{', '.join(accountant.undefined_variables)}",
                )
                raise NameError(msg)

            return True

        except (SyntaxError, NameError):
            return False
