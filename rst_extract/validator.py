"""Validator class definition."""

import ast
from ast import parse

from pydantic import BaseModel, StrictStr


class _DefinedVariableAccountant(ast.NodeVisitor):
    defined_variables: set[StrictStr]
    undefined_variables: set[StrictStr]

    def __init__(self) -> None:
        self.defined_variables = set()
        self.undefined_variables = set()

    def visit_assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.defined_variables.add(target.id)

        self.generic_visit(node)

    def visit_name(self, node: ast.Name) -> None:
        if node.id not in self.defined_variables:
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
