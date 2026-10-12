"""Tests for error paths and defensive branches in the parsers, renderers and helpers.

These cases cannot be written as docstring fixtures, because the public parse
and render entry points never produce the inputs they guard against.
"""

import pytest

from docstring_tailor.cli_config import DocstringStyle
from docstring_tailor.ir_model import (
    DocstringNode,
    NamedParagraph,
    Paragraph,
    SimpleList,
    StructuredList,
    StructuredListParameter,
)
from docstring_tailor.parser.directive_based.sphinx_docstring_parser import (
    SphinxDocstringParser,
)
from docstring_tailor.parser.indentation_based.google_docstring_parser import (
    GoogleDocstringParser,
)
from docstring_tailor.parser.indentation_based.numpy_docstring_parser import (
    NumpyDocstringParser,
)
from docstring_tailor.parser.parser_factory import create_parser
from docstring_tailor.renderer.google_renderer import GoogleDocstringRenderer
from docstring_tailor.renderer.renderer_factory import get_renderer_class
from docstring_tailor.renderer.sphinx_renderer import SphinxDocstringRenderer
from docstring_tailor.utils.utils_formatting import format_code
from docstring_tailor.utils.utils_keyword_translation import translate_keywords
from docstring_tailor.utils.utils_list_detection import (
    _find_ordered_list_start,
    _find_unordered_list_start,
    find_list_start,
    get_list_type,
)
from docstring_tailor.utils.utils_parsing import extract_items, extract_structured_items


class _UnknownNode(DocstringNode):
    """A node type no renderer handles, used to reach the renderer's fallback error."""


# Testing the "create_parser" and "get_renderer_class" functions.


def test_create_parser_rejects_a_style_without_a_parser() -> None:
    """Checks that a style with no parser registered (epydoc) raises ValueError."""
    with pytest.raises(ValueError, match="No parser registered"):
        create_parser(DocstringStyle.epydoc)


def test_get_renderer_class_rejects_a_style_without_a_renderer() -> None:
    """Checks that a style with no renderer registered (epydoc) raises ValueError."""
    with pytest.raises(ValueError, match="No renderer registered"):
        get_renderer_class(DocstringStyle.epydoc)


# Testing the "translate_keywords" function.


def test_translate_keywords_rejects_a_pair_without_a_table() -> None:
    """Checks that translating to or from a style with no table raises ValueError."""
    with pytest.raises(ValueError, match="No keyword translation available"):
        translate_keywords(
            [],
            from_style=DocstringStyle.google,
            to_style=DocstringStyle.epydoc,
        )


# Testing the "format_code" function.


def test_format_code_returns_an_empty_string_for_blank_input() -> None:
    """Checks that a block with no content at all formats to an empty string."""
    assert format_code(text="   \n\n  ", line_separator="\n") == ""


def test_format_code_drops_leading_and_trailing_blank_lines() -> None:
    """Checks that blank lines at both ends of a code block are removed."""
    formatted = format_code(text="\n\n    x = 1\n    y = 2\n\n", line_separator="\n")

    assert formatted == "x = 1\ny = 2"


# Testing the list detection helpers.


def test_find_unordered_list_start_skips_blank_lines_inside_the_block() -> None:
    """Checks that a blank line between two unordered items does not break the run."""
    assert _find_unordered_list_start(["- one", "", "- two"]) == 0


def test_find_unordered_list_start_restarts_after_a_prose_line() -> None:
    """Checks that a prose line resets the run, so a later list is found from its own start."""
    assert _find_unordered_list_start(["- one", "prose", "- two", "- three"]) == 2


def test_find_unordered_list_start_returns_none_for_blank_input() -> None:
    """Checks that a list cannot be found in lines with no content."""
    assert _find_unordered_list_start(["", "   "]) is None


def test_find_ordered_list_start_restarts_when_numbering_breaks() -> None:
    """Checks that a numbering gap resets the run until a valid sequence starts."""
    assert _find_ordered_list_start(["1. one", "3. skipped", "1. one", "2. two"]) == 2


def test_find_ordered_list_start_skips_blank_lines_inside_the_block() -> None:
    """Checks that blank lines between numbered items are ignored."""
    assert _find_ordered_list_start(["1. one", "", "2. two"]) == 0


def test_find_ordered_list_start_returns_none_for_blank_input() -> None:
    """Checks that a numbered list cannot be found in lines with no content."""
    assert _find_ordered_list_start(["  "]) is None


def test_find_list_start_returns_none_when_no_list_exists() -> None:
    """Checks that plain prose contains no list."""
    assert find_list_start("Just prose here.") is None


def test_get_list_type_reports_ordered_lists() -> None:
    """Checks that a numbered list is reported as ordered."""
    assert get_list_type("1. one\n2. two") == "ordered"


# Testing the "extract_items" and "extract_structured_items" functions.


def test_extract_items_returns_nothing_for_empty_content() -> None:
    """Checks that empty section content yields no items."""
    assert extract_items(content="") == []


def test_extract_items_strips_list_markers_and_joins_continuations() -> None:
    """Checks that markers are removed and wrapped continuation lines are joined."""
    items = extract_items(content="- first item\n  continues here\n- second item")

    assert items == ["first item continues here", "second item"]


def test_extract_structured_items_returns_nothing_for_empty_content() -> None:
    """Checks that empty structured content yields no entries."""
    assert extract_structured_items(content="") == []


def test_extract_structured_items_skips_the_header_line_when_asked() -> None:
    """Checks that the keyword line is excluded when skip_first_line is set."""
    items = extract_structured_items(
        content="Args:\n    x (int): A value.", skip_first_line=True
    )

    assert items == [("x (int): A value.", "")]


# Testing the Sphinx parser's defensive branches.


def test_require_directive_raises_for_a_line_without_a_directive() -> None:
    """Checks that asking for a directive on a plain line raises ValueError."""
    with pytest.raises(ValueError, match="Expected an admonition directive"):
        SphinxDocstringParser._require_directive("plain text")


def test_parse_field_block_ignores_a_field_tag_it_does_not_handle() -> None:
    """Checks that a field whose tag matches no group is dropped without an error."""
    nodes = SphinxDocstringParser()._parse_field_block([(":unknown", "text")])

    assert nodes == []


# Testing the parsers' defensive branches.


def test_google_scan_top_level_segments_returns_nothing_for_no_lines() -> None:
    """Checks that scanning empty content yields no segments."""
    assert GoogleDocstringParser()._scan_top_level_segments([], 0) == []


def test_numpy_scan_top_level_segments_returns_nothing_for_no_lines() -> None:
    """Checks that scanning empty content yields no segments."""
    assert NumpyDocstringParser()._scan_top_level_segments([], 0) == []


def test_named_paragraph_body_is_empty_when_it_has_no_content() -> None:
    """Checks that a named paragraph with only whitespace gets an empty body."""
    body = GoogleDocstringParser()._parse_named_paragraph_body("   \n  ")

    assert body == []


# Testing the renderers' defensive branches.


def test_render_node_rejects_a_structured_list_inside_a_named_paragraph() -> None:
    """Checks that a structured list nested in a named paragraph is refused."""
    renderer = GoogleDocstringRenderer(
        line_length=80, current_indent="", indent_unit="    "
    )
    renderer._relative_indent_level = 1
    nested = StructuredList(
        keyword="Args",
        entries=[StructuredListParameter(name="x", type="int", description="Value.")],
    )

    with pytest.raises(ValueError):
        renderer._render_node(nested)


def test_render_node_rejects_an_unknown_node_type() -> None:
    """Checks that a node type with no renderer raises ValueError."""
    renderer = GoogleDocstringRenderer(
        line_length=80, current_indent="", indent_unit="    "
    )

    with pytest.raises(ValueError):
        renderer._render_node(_UnknownNode())


def test_render_opening_paragraph_is_empty_for_blank_text() -> None:
    """Checks that an opening paragraph with no text renders to an empty string."""
    renderer = GoogleDocstringRenderer(
        line_length=80, current_indent="", indent_unit="    "
    )

    assert renderer._render_opening_paragraph("   ") == ""


def test_render_named_paragraph_with_structured_entries_in_a_list_renders_fine() -> (
    None
):
    """Checks that a named paragraph whose body is a simple list still renders."""
    renderer = GoogleDocstringRenderer(
        line_length=80, current_indent="", indent_unit="    "
    )
    node = NamedParagraph(
        header="Note",
        body=[
            SimpleList(
                list_type="unordered", items=["one"], has_leading_blank_line=True
            )
        ],
    )

    rendered = renderer._render_named_paragraph(node)

    assert rendered.startswith("Note:")


def test_sphinx_renderer_hooks_return_their_neutral_values() -> None:
    """Checks the placeholder hooks that Sphinx satisfies without using them."""
    renderer = SphinxDocstringRenderer(
        line_length=80, current_indent="", indent_unit="    "
    )
    entry = StructuredListParameter(name="x", type=None, description="Value.")

    assert renderer._section_body_indented is False
    assert renderer._render_section_header("Args") == "Args"
    assert renderer._render_structured_list_entry(entry) == ""
    assert renderer._join_rendered_nodes([], []) == ""


def test_sphinx_renderer_joins_a_paragraph_and_a_list_without_a_blank_line() -> None:
    """Checks the Sphinx junction rule for a list that follows prose directly."""
    renderer = SphinxDocstringRenderer(
        line_length=80, current_indent="", indent_unit="    "
    )
    nodes: list[DocstringNode] = [
        Paragraph(content="Prose."),
        SimpleList(list_type="unordered", items=["one"], has_leading_blank_line=False),
    ]

    joined = renderer._join_rendered_nodes(nodes, ["Prose.", "- one"])

    assert joined == "Prose.\n- one"
