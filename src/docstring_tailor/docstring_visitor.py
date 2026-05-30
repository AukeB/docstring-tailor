"""Module providing functionality to format Python docstrings into the Google Docstring format."""

import re

import libcst as cst

from src.docstring_tailor.constants import (
    DOCSTRING_DELIMITER,
    DOCSTRING_DELIMITER_LENGTH,
)
from src.docstring_tailor.docstring_section_formatter import DocstringSectionFormatter


class DocstringVisitor(cst.CSTTransformer):
    """A transformer for handling and formatting docstrings into the Google Docstring format.

    This class uses `libcst` to traverse and modify Python source code. It identifies docstrings
    and transforms them into the desired format.
    """

    def __init__(self, line_length: int) -> None:
        """Initialises the DocstringVisitor.

        Sets up the indentation tracker used to correctly format multi-line docstrings at any
        nesting level.

        Args:
            line_length (int): Maximum characters per line including indentation and/or triple
                quotes.
        """
        self.line_length = line_length
        self._current_indent = ""
        self._indent_unit = "    "

    def visit_Module(self, node: cst.Module) -> None:
        """Captures the default indentation unit from the module on first entry.

        Args:
            node (cst.Module): The root module node.
        """
        self._indent_unit = node.default_indent

    def _is_docstring(self, node: cst.SimpleStatementLine) -> bool:
        """Determines if a given node is a docstring.

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

    def visit_IndentedBlock(self, node: cst.IndentedBlock) -> None:
        """Tracks the current indentation level when entering an indented block.

        Args:
            node (cst.IndentedBlock): The indented block node being visited.
        """
        self._current_indent += self._indent_unit

    def leave_IndentedBlock(
        self,
        original_node: cst.IndentedBlock,
        updated_node: cst.IndentedBlock,
    ) -> cst.IndentedBlock:
        """Restores the current indentation level when leaving an indented block.

        Args:
            original_node (cst.IndentedBlock): The original indented block node.
            updated_node (cst.IndentedBlock): The updated indented block node.

        Returns:
            updated_node (cst.IndentedBlock): The updated node, unchanged.
        """
        self._current_indent = self._current_indent[: -len(self._indent_unit)]

        return updated_node

    def _build_raw_multiline_docstring(self, content: str) -> str:
        """Builds a raw multi-line docstring string from the stripped content.

        Delegates formatting to DocstringSectionFormatter, which handles plain paragraphs and
        named sections such as Args, Returns, and Raises independently.

        Args:
            content (str): The stripped docstring content, excluding the triple quote delimiters.

        Returns:
            raw (str): The formatted raw multi- line docstring string including the triple quote
                delimiters.
        """
        section_formatter = DocstringSectionFormatter(
            line_length=self.line_length,
            current_indent=self._current_indent,
            indent_unit=self._indent_unit,
        )

        joined_content = section_formatter.format(content=content)

        raw = (
            DOCSTRING_DELIMITER
            + joined_content
            + "\n"
            + self._current_indent
            + DOCSTRING_DELIMITER
        )

        return raw

    def _build_raw_docstring(self, content: str) -> str:
        """Builds the raw docstring string from the stripped content.

        A docstring is placed on one line if it fits within the line length and the user has not
        deliberately introduced paragraph breaks. Otherwise delegates to
        _build_raw_multiline_docstring.

        Args:
            content (str): The stripped docstring content, excluding the triple quote delimiters.

        Returns:
            raw (str): The formatted raw docstring string including the triple quote delimiters.
        """
        is_deliberately_multiline = bool(re.search(r"\n\s*\n", content))
        normalized_content = re.sub(r"\s+", " ", content.strip())
        fits_on_one_line = (
            len(self._current_indent)
            + len(normalized_content)
            + 2 * DOCSTRING_DELIMITER_LENGTH
            <= self.line_length
        )

        if fits_on_one_line and not is_deliberately_multiline:
            raw = DOCSTRING_DELIMITER + normalized_content + DOCSTRING_DELIMITER
        else:
            raw = self._build_raw_multiline_docstring(content=content)

        return raw

    def _format_docstring(
        self, node: cst.SimpleStatementLine
    ) -> cst.SimpleStatementLine:
        """Formats a docstring node by wrapping its content to the configured line length.

        Single-line docstrings have the closing triple quotes on the same line. Multi- line
        docstrings have the closing triple quotes on a new line.

        Args:
            node (cst.SimpleStatementLine): A CST node containing a docstring.

        Returns:
            updated_node (cst.SimpleStatementLine): The updated node with the formatted docstring.
        """
        # Extract content
        raw_string_value = node.body[0].value.value  # type: ignore
        content = raw_string_value[
            DOCSTRING_DELIMITER_LENGTH:-DOCSTRING_DELIMITER_LENGTH
        ].strip()

        # print(raw_string_value)
        # print(repr(content))

        # Build and apply raw string
        new_raw = self._build_raw_docstring(content=content)

        # print("\n")

        # Update node
        new_string_node = cst.SimpleString(new_raw)
        new_expr = node.body[0].with_changes(value=new_string_node)
        updated_node = node.with_changes(body=(new_expr,))

        return updated_node

    def leave_SimpleStatementLine(
        self,
        original_node: cst.SimpleStatementLine,
        updated_node: cst.SimpleStatementLine,
    ) -> (
        cst.BaseStatement | cst.FlattenSentinel[cst.BaseStatement] | cst.RemovalSentinel
    ):
        """Processes a simple statement line during traversal and handles docstrings.

        Args:
            original_node (cst.SimpleStatementLine): The original CST node.
            updated_node (cst.SimpleStatementLine): The updated CST node.

        Returns:
            cst.BaseStatement: The final statement after transformation.
        """
        if self._is_docstring(node=updated_node):
            updated_node = self._format_docstring(node=updated_node)

        return super().leave_SimpleStatementLine(original_node, updated_node)
