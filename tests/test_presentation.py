"""Smoke tests for the marimo presentation in ``presentation/presentation.py``.

The notebook calls DocstringVisitor directly, so these tests catch a change to the
formatter that would break the talk: a cell that raises, or output that grows so
much that it no longer fits in the code box on a slide.
"""

import pytest

from docstring_tailor.cli_config import DocstringStyle
from presentation.presentation import app


NotebookDefs = dict[str, object]

# Positions within each slide's line-length range: both ends, next to both ends, and 88.
_RANGE_POSITIONS = ["min", "min+1", "88", "max-1", "max"]
_SLIDES = ["simple", "complex", "convert"]


def _length_at(notebook_defs: NotebookDefs, slide: str, position: str) -> int:
    """Returns the line length at a named position in a slide's line-length range."""
    minimum, maximum = notebook_defs["LENGTH_RANGES"][slide]

    lengths = {
        "min": minimum,
        "min+1": minimum + 1,
        "88": 88,
        "max-1": maximum - 1,
        "max": maximum,
    }

    length = lengths[position]

    return length


@pytest.fixture(scope="module")
def notebook_defs() -> NotebookDefs:
    """Runs every cell of the notebook once, and returns the names it defines.

    app.run() raises the error of the first cell that fails, so running it is
    already the main check.
    """
    _outputs, defs = app.run()
    notebook_names = dict(defs)

    return notebook_names


# Testing the "presentation" notebook as a whole.


@pytest.mark.parametrize("slide", _SLIDES)
def test_notebook_loads_an_example_module_for_every_slide(
    notebook_defs: NotebookDefs,
    slide: str,
) -> None:
    """Checks that each live slide's example module is read from the notebook's folder."""
    sources = notebook_defs["sources"]

    assert "def " in sources[slide]


# Testing the "format_source" function.


@pytest.mark.parametrize("slide", _SLIDES)
@pytest.mark.parametrize("style", [DocstringStyle.google, DocstringStyle.numpy])
@pytest.mark.parametrize("position", _RANGE_POSITIONS)
def test_format_source_returns_valid_python(
    notebook_defs: NotebookDefs,
    slide: str,
    style: DocstringStyle,
    position: str,
) -> None:
    """Checks that formatting and converting each example still produce valid Python."""
    format_source = notebook_defs["format_source"]
    source = notebook_defs["sources"][slide]
    length = _length_at(notebook_defs, slide, position)
    formatted = format_source(source, length, style)

    compile(formatted, f"{slide}_module.py", "exec")


# Testing the "fixed_font_size" function.


@pytest.mark.parametrize("slide", _SLIDES)
@pytest.mark.parametrize("position", _RANGE_POSITIONS)
def test_fixed_font_size_fits_the_code_at_every_line_length(
    notebook_defs: NotebookDefs,
    slide: str,
    position: str,
) -> None:
    """Checks that no slide's code box overflows at any line length in the slider range."""
    length = _length_at(notebook_defs, slide, position)
    format_source = notebook_defs["format_source"]
    fit_font_size = notebook_defs["fit_font_size"]
    render_code = notebook_defs["render_code"]
    source = notebook_defs["sources"][slide]
    box = notebook_defs["CODE_BOXES"][slide]
    font_size = notebook_defs["font_sizes"][slide]

    for style in notebook_defs["SLIDE_STYLES"][slide]:
        code = format_source(source, length, style)
        size_for_this_code = fit_font_size(code, length, box)
        block = render_code(code, length, font_size, box[1])

        assert "<pre" in block
        assert font_size <= size_for_this_code + 1e-9


# Testing the "sweep_length" function.


@pytest.mark.parametrize(
    ("tick", "expected_length"),
    [
        (0, 120),
        (1, 119),
        (90, 30),
        (91, 31),
        (180, 120),
    ],
)
def test_sweep_length_goes_down_to_the_minimum_and_back(
    notebook_defs: NotebookDefs,
    tick: int,
    expected_length: int,
) -> None:
    """Checks that the complex slide's auto-sweep runs from 120 down to 30 and back up."""
    sweep_length = notebook_defs["sweep_length"]
    length_range = notebook_defs["LENGTH_RANGES"]["complex"]

    assert sweep_length(tick, length_range) == expected_length
