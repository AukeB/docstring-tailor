"""Obtains all docstrings in a python module."""

import libcst as cst

from docstring_tailor.cli_config import DocstringStyle
from docstring_tailor.constants import DOCSTRING_DELIMITER
from docstring_tailor.parser.parser_factory import create_parser
from docstring_tailor.renderer.renderer_factory import get_renderer_class
from docstring_tailor.utils.utils_keyword_translation import translate_keywords


class DocstringVisitor(cst.CSTTransformer):
    """A transformer for traversing and rendering docstrings.

    Subclasses libcst's CSTTransformer, which implements the visitor pattern
    over a Concrete Syntax Tree (CST). When tree.visit(DocstringVisitor()) is
    called, libcst traverses every node in the tree and automatically dispatches
    to the corresponding visit_* or leave_* method on this class if one exists.
    Method names are derived directly from the CST node class names — for
    example, visit_IndentedBlock is called for every cst.IndentedBlock node
    encountered. visit_* methods are called on entry into a node (pre-order) and
    leave_* methods are called on exit (post-order). leave_* methods receive
    both the original and updated node, and their return value replaces the node
    in the reconstructed tree.

    The visit_* methods in this class (visit_Module, visit_IndentedBlock) are
    used exclusively to track indentation state as the tree is traversed, not to
    modify it. leave_IndentedBlock is similarly used only for indentation
    tracking. Modifications to the tree happen only in
    leave_SimpleStatementLine.

    Workflow: The entry point for all transformations is
    leave_SimpleStatementLine, called for every simple statement encountered. It
    delegates to _is_docstring to determine whether the statement is a
    docstring. If not, the node is returned unchanged via the super() call. If
    it is, the node is passed to _process_docstring_node, which extracts the raw
    string content and passes it to _transform_docstring. There, the content is
    parsed into a typed IR by the from_style parser, translated to to_style's
    keyword vocabulary if the two styles differ, then rendered back into a
    formatted docstring string by the to_style renderer.

    Attributes:
        _line_length (int): Maximum characters per line including indentation
            and triple double quotes.
        _current_indent (str): The accumulated indentation string at the current
            nesting level, updated as the tree is traversed.
        _indent_unit (str): The indentation unit string used in the source file,
            captured from the module node on entry. Initialised to four spaces
            as a safety placeholder.
        _from_style (DocstringStyle): The style docstrings are parsed as.
        _to_style (DocstringStyle): The style docstrings are rendered as. Equal
            to _from_style for a same-style format, different for a convert.
        _parser (IndentationBasedParser): Reusable parser instance for
            _from_style, instantiated once since the parser is stateless across
            docstrings.
        _renderer_class (type[DocstringRendererBase]): The renderer class for
            _to_style. Not instantiated here -- a fresh renderer is built per
            docstring in _transform_docstring, since it depends on
            _current_indent, which changes as the tree is traversed.
    """

    def __init__(
        self,
        line_length: int,
        from_style: DocstringStyle,
        to_style: DocstringStyle,
    ) -> None:
        """Initialises the DocstringVisitor.

        Sets up the indentation tracker used to correctly render multi-line
        docstrings at any nesting level. The initial value of _indent_unit is a
        four-space placeholder for safety, as it will always be overwritten by
        visit_Module before any docstring is processed. The parser is
        instantiated once here since it is stateless across docstrings; the
        renderer class is looked up but not instantiated, since a renderer
        instance is built fresh per docstring.

        Args:
            line_length (int): Maximum characters per line including indentation
                and triple double quotes.
            from_style (DocstringStyle): The style to parse docstrings as.
            to_style (DocstringStyle): The style to render docstrings as. Pass
                the same value as from_style for a same-style format; a
                different value performs a style conversion.
        """
        self._line_length = line_length
        self._current_indent = ""
        self._indent_unit = "    "
        self._from_style = from_style
        self._to_style = to_style
        self._parser = create_parser(from_style)
        self._renderer_class = get_renderer_class(to_style)

    def visit_Module(self, node: cst.Module) -> None:
        """Captures the default indentation unit from the module on first entry.

        Called automatically by libcst when entering the root Module node,
        before any other node is visited. Overwrites the placeholder
        _indent_unit set in __init__ with the actual indentation string used in
        the source file.

        Args:
            node (cst.Module): The root module node.
        """
        self._indent_unit = node.default_indent

    def visit_IndentedBlock(self, node: cst.IndentedBlock) -> None:
        """Tracks the current indentation level when entering an indented block.

        Called automatically by libcst each time it enters a cst.IndentedBlock
        node, such as the body of a function, class, or control flow statement.
        Accumulates the indentation depth by appending one indent unit to
        _current_indent.

        Args:
            node (cst.IndentedBlock): The indented block node being visited.
        """
        self._current_indent += self._indent_unit

    def leave_IndentedBlock(
        self,
        original_node: cst.IndentedBlock,
        updated_node: cst.IndentedBlock,
    ) -> cst.IndentedBlock:
        """Restores the current indentation level when leaving an indented
        block.

        Called automatically by libcst each time it exits a cst.IndentedBlock
        node. Counterpart to visit_IndentedBlock — strips one indent unit from
        _current_indent to restore the indentation level of the enclosing scope.

        Args:
            original_node (cst.IndentedBlock): The original indented block node.
            updated_node (cst.IndentedBlock): The updated indented block node.

        Returns:
            updated_node (cst.IndentedBlock): The updated node, unchanged.
        """
        self._current_indent = self._current_indent[: -len(self._indent_unit)]

        return updated_node

    def _transform_docstring(self, content: str) -> str:
        """Parses and renders a raw docstring string into its formatted
        equivalent.

        Keyword translation only runs when _from_style and _to_style differ,
        since a same-style format has nothing to translate and the two keyword-
        translation tables are only defined for cross-style pairs.

        Args:
            content (str): The raw docstring string including triple-quote
                delimiters.

        Returns:
            rendered (str): The fully rendered docstring string.
        """
        ir = self._parser.parse(content=content)

        if self._from_style != self._to_style:
            ir = translate_keywords(
                ir, from_style=self._from_style, to_style=self._to_style
            )

        renderer = self._renderer_class(
            line_length=self._line_length,
            current_indent=self._current_indent,
            indent_unit=self._indent_unit,
        )

        rendered = renderer.render(ir=ir)

        return rendered

    def _process_docstring_node(
        self, node: cst.SimpleStatementLine
    ) -> cst.SimpleStatementLine:
        """Extracts, transforms, and reattaches the rendered docstring on the
        given CST node.

        Extracts the raw string value from the CST node and passes it to
        _transform_docstring. The result is then wrapped back into the
        appropriate CST node types and reattached to the statement.

        Args:
            node (cst.SimpleStatementLine): A CST node containing a docstring.

        Returns:
            updated_node (cst.SimpleStatementLine): The updated node with the
                rendered docstring.
        """
        # Extract
        raw_docstring = node.body[0].value.value  # type: ignore

        # Transform
        rendered_docstring = self._transform_docstring(content=raw_docstring)

        # Reattach
        updated_simple_string = cst.SimpleString(rendered_docstring)
        updated_expression = node.body[0].with_changes(value=updated_simple_string)
        updated_node = node.with_changes(body=(updated_expression,))

        return updated_node

    def _is_docstring(self, node: cst.SimpleStatementLine) -> bool:
        """Determines if a given node is a docstring.

        Checks that the statement contains exactly one expression, that the
        expression is a simple string, and that the string begins with the
        triple quote delimiter.

        Args:
            node (cst.SimpleStatementLine): A node in the CST representing a
                statement.

        Returns:
            is_docstring (bool): True if the node is a docstring, False
                otherwise.
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
        """Processes a simple statement line during traversal and formats it if
        it is a docstring.

        Called automatically by libcst for every simple statement in the file.
        Acts as the entry point for all docstring transformations. If the
        statement is not a docstring, the node is returned unchanged via the
        super() call. If it is, it is passed to _process_docstring_node for
        formatting.

        Args:
            original_node (cst.SimpleStatementLine): The original CST node.
            updated_node (cst.SimpleStatementLine): The updated CST node.

        Returns:
            node (cst.BaseStatement): The final statement after transformation.
        """
        if self._is_docstring(node=updated_node):
            updated_node = self._process_docstring_node(node=updated_node)

        return super().leave_SimpleStatementLine(original_node, updated_node)
