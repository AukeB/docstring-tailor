"""Module providing functionality to format Python docstrings into the Google Docstring format."""

import textwrap

import libcst as cst

from src.docstring_tailor.constants import (
    DOCSTRING_DELIMITER,
    DOCSTRING_DELIMITER_LENGTH,
    LINE_LENGTH,
)


class DocstringVisitor(cst.CSTTransformer):
    """
    A transformer for handling and formatting docstrings into the Google Docstring format.

    This class uses `libcst` to traverse and modify Python source code. It identifies docstrings
    and transforms them into the desired format.
    """

    def _is_docstring(self, node: cst.SimpleStatementLine) -> bool:
        """
        Determines if a given node is a docstring.

        Args:
            node (cst.SimpleStatementLine): A node in the CST representing a statement.

        Returns:
            bool: True if the node is a docstring, False otherwise.
        """
        is_docstring: bool = (
            len(node.body) == 1
            and isinstance(node.body[0], cst.Expr)
            and isinstance(node.body[0].value, cst.SimpleString)
            and node.body[0].value.value.startswith(DOCSTRING_DELIMITER)
        )

        return is_docstring

    def leave_SimpleStatementLine(
        self,
        original_node: cst.SimpleStatementLine,
        updated_node: cst.SimpleStatementLine,
    ) -> (
        cst.BaseStatement | cst.FlattenSentinel[cst.BaseStatement] | cst.RemovalSentinel
    ):
        """
        Processes a simple statement line during traversal and handles docstrings.

        Args:
            original_node (cst.SimpleStatementLine): The original CST node.
            updated_node (cst.SimpleStatementLine): The updated CST node.

        Returns:
            cst.BaseStatement: The final statement after transformation.
        """
        if self._is_docstring(node=updated_node):
            raw_string_value = updated_node.body[0].value.value  # type: ignore
            content = raw_string_value[
                DOCSTRING_DELIMITER_LENGTH:-DOCSTRING_DELIMITER_LENGTH
            ].strip()

            wrapped_lines = textwrap.wrap(
                content, width=LINE_LENGTH - DOCSTRING_DELIMITER_LENGTH
            )
            new_raw = (
                DOCSTRING_DELIMITER
                + "\n".join(wrapped_lines)
                + "\n"
                + DOCSTRING_DELIMITER
            )

            new_string_node = cst.SimpleString(new_raw)
            new_expr = updated_node.body[0].with_changes(value=new_string_node)
            updated_node = updated_node.with_changes(body=(new_expr,))

        return super().leave_SimpleStatementLine(original_node, updated_node)
