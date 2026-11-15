import marimo

__generated_with = "0.25.2"
app = marimo.App(
    width="medium",
    layout_file="layouts/presentation.slides.json",
)


@app.cell
def _():
    import difflib
    import html
    import re

    import libcst as cst
    import marimo as mo
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import PythonLexer, YamlLexer

    from docstring_tailor.cli_config import DocstringStyle
    from docstring_tailor.docstring_visitor import DocstringVisitor

    return (
        DocstringStyle,
        DocstringVisitor,
        HtmlFormatter,
        PythonLexer,
        YamlLexer,
        cst,
        difflib,
        highlight,
        html,
        mo,
        re,
    )


@app.cell
def _(text_slide):
    text_slide("""
    # docstring-tailor 🪡

    ## Formatting the text inside your docstrings

    Auke Bruinsma

    [github.com/AukeB/docstring-tailor](https://github.com/AukeB/docstring-tailor)
    """)
    return


@app.cell
def _(mo):
    mo.Html(
        """
        <div style="display:flex; flex-direction:column; justify-content:center;
                    align-items:center; min-height:560px; text-align:center;">
          <p style="font-size:44px; line-height:1.3; margin:0;">
            Ruff formats your code.<br>
            <b>Who formats your docstrings?</b>
          </p>
        </div>
        """
    )
    return


@app.cell
def _(text_slide):
    # The note is a plain HTML box: markdown block syntax and mo.callout both break in
    # the PDF export.
    text_slide("""
    ## This presentation is a Python module

    - **marimo**: a reactive Python notebook, an alternative to Jupyter, stored as a
      plain `.py` file.
    - **Interactive elements** such as sliders and dropdowns rerun every cell that
      depends on them.
    - **A slides mode**: every cell with output can become a slide.
    - **It can load `.py` modules** and render them: the next slides read example
      modules and run docstring-tailor on them live.

    <div style="margin-top:18px; padding:12px 16px; border-left:5px solid #d4a72c;
                border-radius:6px; background:#fff8c5; color:#1f2328;">
    <b>Demonstration only.</b> The recommended way to use docstring-tailor is the CLI
    or a pre-commit hook. At the end we go over the commands and how to configure it
    for your codebase.
    </div>
    """)
    return


@app.cell
def _(mo):
    _examples = mo.notebook_dir() / "examples"

    sources = {
        "simple": (_examples / "simple_module.py").read_text(encoding="utf-8"),
        "complex": (_examples / "complex_module.py").read_text(encoding="utf-8"),
        "convert": (_examples / "example_module.py").read_text(encoding="utf-8"),
    }
    return (sources,)


@app.cell
def _(mo):
    # The font sizes are computed from this range, so a higher minimum gives larger fonts.
    LINE_LENGTH_MIN = 50
    LINE_LENGTH_MAX = 120
    # The simple slide and the complex slide's auto-sweep go further down.
    SHORT_LINE_LENGTH_MIN = 30

    line_length = mo.ui.slider(
        start=SHORT_LINE_LENGTH_MIN,
        stop=LINE_LENGTH_MAX,
        value=88,
        step=1,
        label="Line length",
        show_value=True,
        full_width=True,
    )
    return LINE_LENGTH_MAX, LINE_LENGTH_MIN, SHORT_LINE_LENGTH_MIN, line_length


@app.cell
def _(
    DocstringStyle,
    DocstringVisitor,
    HtmlFormatter,
    LINE_LENGTH_MAX,
    LINE_LENGTH_MIN,
    PythonLexer,
    cst,
    highlight,
    mo,
):
    LINE_HEIGHT = 1.35
    # Width of one monospace character relative to the font size.
    CHAR_WIDTH = 0.6
    PADDING = 16
    RULER_COLOR = "#e5534b"
    TEXT_SLIDE_FONT_SIZE = "22px"

    def text_slide(markdown: str, font_size: str = TEXT_SLIDE_FONT_SIZE) -> object:
        """Renders a markdown text slide at a font size that reads well on a projector."""
        slide = mo.md(markdown).style({"font-size": font_size})

        return slide

    def format_source(
        source: str,
        length: int,
        to_style: DocstringStyle = DocstringStyle.google,
    ) -> str:
        """Formats the Google-style docstrings in source, optionally converting them."""
        visitor = DocstringVisitor(
            line_length=length,
            from_style=DocstringStyle.google,
            to_style=to_style,
        )

        tree = cst.parse_module(source)
        formatted = tree.visit(visitor).code

        return formatted

    def fit_font_size(code: str, length: int, box: tuple[int, int]) -> float:
        """Returns the largest font size at which this code fits in a (width, height) box."""
        box_width, box_height = box
        lines = code.splitlines()
        line_lengths = [len(line) for line in lines]
        columns = max(length, *line_lengths) + 1

        size_by_height = (box_height - 2 * PADDING) / (len(lines) * LINE_HEIGHT)
        size_by_width = (box_width - 2 * PADDING) / (columns * CHAR_WIDTH)
        font_size = min(size_by_height, size_by_width)

        return font_size

    def fixed_font_size(
        source: str,
        styles: list[DocstringStyle],
        box: tuple[int, int],
        length_range: tuple[int, int] = (LINE_LENGTH_MIN, LINE_LENGTH_MAX),
    ) -> float:
        """Returns one font size at which every style fits across the whole length range.

        The shortest line length gives the tallest code, and the longest line length
        gives the widest code, so only those two need to be checked.
        """
        sizes = []

        for style in styles:
            for length in length_range:
                code = format_source(source, length, style)
                size = fit_font_size(code, length, box)
                sizes.append(size)

        font_size = min(sizes)

        return font_size

    def render_code(code: str, length: int, font_size: float, height: int) -> str:
        """Renders highlighted code in a fixed-height box with a ruler at the given column."""
        formatter = HtmlFormatter(nowrap=True, noclasses=True, style="friendly")
        highlighted = highlight(code, PythonLexer(), formatter)

        edge = f"calc({PADDING}px + {length}ch)"
        ruler = (
            f"linear-gradient(to right, transparent {edge}, {RULER_COLOR} {edge}, "
            f"{RULER_COLOR} calc({edge} + 2px), transparent calc({edge} + 2px))"
        )

        block = (
            f'<pre style="font-family: monospace; font-size: {font_size:.1f}px; '
            f"line-height: {LINE_HEIGHT}; padding: {PADDING}px; margin: 0; "
            f"height: {height}px; box-sizing: border-box; "
            f"overflow: hidden; border-radius: 6px; "
            f'background: {ruler}, #f6f8fa; color: #1f2328;">{highlighted}</pre>'
        )

        return block

    def sweep_length(tick: int, length_range: tuple[int, int]) -> int:
        """Returns the line length for an auto-sweep tick, going from max to min and back."""
        minimum, maximum = length_range
        span = maximum - minimum
        position = tick % (2 * span)

        if position <= span:
            length = maximum - position
        else:
            length = minimum + (position - span)

        return length

    return (
        fit_font_size,
        fixed_font_size,
        format_source,
        render_code,
        sweep_length,
        text_slide,
    )


@app.cell
def _(
    DocstringStyle,
    LINE_LENGTH_MAX,
    LINE_LENGTH_MIN,
    SHORT_LINE_LENGTH_MIN,
    fixed_font_size,
    sources,
):
    # Space for the code on each slide, as (width, height) in px on the 1280x720 canvas.
    # Lower a height if the bottom of that slide's code is cut off.
    CODE_BOXES = {
        "simple": (1180, 520),
        "complex": (700, 640),
        "convert": (1180, 580),
    }

    # Line-length range per slide.
    LENGTH_RANGES = {
        "simple": (SHORT_LINE_LENGTH_MIN, LINE_LENGTH_MAX),
        "complex": (SHORT_LINE_LENGTH_MIN, LINE_LENGTH_MAX),
        "convert": (LINE_LENGTH_MIN, LINE_LENGTH_MAX),
    }

    CONVERT_STYLES = {"Google": DocstringStyle.google, "NumPy": DocstringStyle.numpy}

    SLIDE_STYLES = {
        "simple": [DocstringStyle.google],
        "complex": [DocstringStyle.google],
        "convert": list(CONVERT_STYLES.values()),
    }

    # One font size per slide, fixed across its whole slider range and all its styles.
    font_sizes = {
        name: fixed_font_size(sources[name], SLIDE_STYLES[name], box, LENGTH_RANGES[name])
        for name, box in CODE_BOXES.items()
    }
    return CODE_BOXES, CONVERT_STYLES, LENGTH_RANGES, SLIDE_STYLES, font_sizes


@app.cell
def _(CODE_BOXES, font_sizes, format_source, line_length, mo, render_code, sources):
    _length = line_length.value
    _code = format_source(sources["simple"], _length)
    _block = render_code(_code, _length, font_sizes["simple"], CODE_BOXES["simple"][1])

    mo.vstack([mo.md("### A simple docstring"), line_length, mo.Html(_block)])
    return


@app.cell
def _(mo):
    # Starts switched off. Pick a speed in the dropdown to start, and "off" to pause.
    sweep_ticker = mo.ui.refresh(options=["0.1s", "0.2s", "0.5s"], label="Auto-sweep")
    return (sweep_ticker,)


@app.cell
def _(
    CODE_BOXES,
    LENGTH_RANGES,
    font_sizes,
    format_source,
    mo,
    re,
    render_code,
    sources,
    sweep_length,
    sweep_ticker,
):
    # The ticker's value looks like "0.2s (37)": the number counts the ticks.
    _match = re.search(r"\((\d+)\)$", sweep_ticker.value)
    _tick = int(_match.group(1)) if _match else 0
    _length = sweep_length(_tick, LENGTH_RANGES["complex"])

    _code = format_source(sources["complex"], _length)
    _block = render_code(_code, _length, font_sizes["complex"], CODE_BOXES["complex"][1])

    _panel = mo.vstack(
        [
            mo.md("### A complex Google docstring"),
            mo.hstack([sweep_ticker, mo.md(f"**Line length: {_length}**")], justify="start", gap=1),
            mo.md("""
    **Kept intact while wrapping:**

    - Summary line, and the blank lines between parts
    - Indentation of arguments, returns and errors
    - Continuation lines one level deeper
    - Lists: one item per line, hanging indent
    - `>>>` examples and fenced code blocks, never reflowed
    - Section names, such as `Note:` and `Examples:`

    Based on the
    [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings),
    the starting point for all parsing and rendering rules.
    """).style({"font-size": "17px"}),
        ],
        gap=1,
    )

    mo.hstack([mo.Html(_block), _panel], widths=[3, 2], align="start", gap=1.5)
    return


@app.cell
def _(mo):
    _box = (
        "padding:10px 14px; border-radius:8px; border:2px solid {color}; "
        "background:{fill}; text-align:center; font-size:18px; line-height:1.3;"
    )
    _plain = _box.format(color="#8c959f", fill="#f6f8fa")
    _parse = _box.format(color="#3b6ea8", fill="#e6eef7")
    _ir = _box.format(color="#8250df", fill="#f3eefc")
    _render = _box.format(color="#1a7f37", fill="#dafbe1")
    _arrow = '<div style="font-size:26px; color:#8c959f;">→</div>'
    _row = 'style="display:flex; align-items:center; gap:10px; justify-content:center;"'

    _ir_nodes = ", ".join(
        [
            "Paragraph",
            "StructuredList",
            "SimpleList",
            "NamedParagraph",
            "CodeBlock",
            "CodeREPL",
        ]
    )

    mo.Html(
        f"""
        <h2 style="margin:0 0 18px;">How it works</h2>

        <div {_row}>
          <div style="{_plain}">Version 1<br><small>a formatter that edited<br>the text directly</small></div>
          {_arrow}
          <div style="{_plain}">Rewritten</div>
          {_arrow}
          <div style="{_parse}"><b>Now</b><br><small>parse → IR → render</small></div>
        </div>

        <div style="height:34px;"></div>

        <div {_row}>
          <div style="{_plain}">.py file</div>
          {_arrow}
          <div style="{_plain}">LibCST<br><small>finds the docstrings</small></div>
          {_arrow}
          <div style="{_parse}"><b>Parser</b><br><small>Google · NumPy</small></div>
          {_arrow}
          <div style="{_ir}"><b>IR</b><br><small>style-agnostic<br>structure</small></div>
          {_arrow}
          <div style="{_render}"><b>Renderer</b><br><small>Google · NumPy</small></div>
          {_arrow}
          <div style="{_plain}">LibCST<br><small>writes the file back</small></div>
        </div>

        <p style="text-align:center; color:#59636e; font-size:16px; margin:14px 0 0;">
          IR nodes: {_ir_nodes}
        </p>

        <p style="text-align:center; font-size:26px; margin:40px 0 0;">
          Wrapping is the easy part. <b>Recognising structure is the hard part.</b>
        </p>
        """
    )
    return


@app.cell
def _(CONVERT_STYLES, LINE_LENGTH_MAX, LINE_LENGTH_MIN, mo):
    target_style = mo.ui.dropdown(options=CONVERT_STYLES, value="Google", label="Style")

    convert_line_length = mo.ui.slider(
        start=LINE_LENGTH_MIN,
        stop=LINE_LENGTH_MAX,
        value=88,
        step=1,
        label="Line length",
        show_value=True,
        full_width=True,
    )
    return convert_line_length, target_style


@app.cell
def _(
    CODE_BOXES,
    convert_line_length,
    font_sizes,
    format_source,
    mo,
    render_code,
    sources,
    target_style,
):
    _length = convert_line_length.value
    _code = format_source(sources["convert"], _length, target_style.value)
    _block = render_code(_code, _length, font_sizes["convert"], CODE_BOXES["convert"][1])

    mo.vstack(
        [
            mo.hstack([target_style, convert_line_length], widths=[1, 4], align="center"),
            mo.Html(_block),
        ]
    )
    return


@app.cell
def _(difflib, format_source, html, mo, sources):
    # A real --diff output: the simple example, formatted at line length 60, reformatted
    # to 50. Short lines and no context lines (n=0) keep it narrow enough for the PDF.
    _original = format_source(sources["simple"], 60)
    _formatted = format_source(_original, 50)

    _diff_lines = difflib.unified_diff(
        _original.splitlines(keepends=True),
        _formatted.splitlines(keepends=True),
        fromfile="greet.py (original)",
        tofile="greet.py (formatted)",
        n=0,
    )

    _colours = {"+": "#1a7f37", "-": "#cf222e", "@": "#8250df"}
    _rendered = []

    for _line in _diff_lines:
        _colour = _colours.get(_line[:1], "#1f2328")
        _weight = "bold" if _line.startswith(("---", "+++")) else "normal"
        _escaped = html.escape(_line.rstrip("\n"))
        _rendered.append(f'<span style="color:{_colour}; font-weight:{_weight};">{_escaped}</span>')

    _diff_html = "\n".join(_rendered)

    _features = mo.md("""
    ## More features

    - **`--diff`** shows the changes and writes nothing. It exits with code 1 when
      something would change: a CI gate.
    - **`--exclude`** skips paths by name or glob. Can be repeated.
    - **Paths**: files and folders, several at once. Default: `src/`.
    - **Config** in `pyproject.toml` or `docstring_tailor.toml`. Command-line
      options win.
    - **Line length** 30 to 300, default 100. **Style** is always explicit.
    """).style({"font-size": "17px"})

    _diff_block = mo.Html(
        '<p style="margin:0 0 6px; font-size:15px; color:#59636e;">'
        "docstring_tailor format greet.py --line-length 50 --diff</p>"
        '<pre style="font-family:monospace; font-size:11px; line-height:1.35; margin:0; '
        'padding:12px; border-radius:6px; background:#f6f8fa; white-space:pre; overflow:hidden;">'
        f"{_diff_html}</pre>"
    )

    mo.hstack([_features, _diff_block], widths=[1, 1.2], align="start", gap=1.5)
    return


@app.cell
def _(HtmlFormatter, YamlLexer, highlight, mo, text_slide):
    _commands = text_slide(
        """
    ## Use it in your project

    ```bash
    # Install as a dev dependency
    uv add --dev docstring-tailor

    # Format docstrings in place
    uv run docstring_tailor format src/

    # Check only, for CI: writes nothing, exits 1 on changes
    uv run docstring_tailor format src/ --diff

    # Migrate between styles, once
    uv run docstring_tailor convert src/ \\
        --from-style google --to-style numpy
    ```

    ```toml
    # pyproject.toml
    [tool.docstring_tailor]
    line-length = 88
    style = "google"
    exclude = ["tests"]
    ```
    """,
        font_size="17px",
    )

    # Highlighted directly with Pygments: marimo's markdown mangles the indentation of
    # lines that start with "- " inside a code block.
    _hook_config = (
        "# .pre-commit-config.yaml\n"
        "repos:\n"
        "  - repo: https://github.com/AukeB/docstring-tailor\n"
        "    rev: v0.4.1\n"
        "    hooks:\n"
        "      - id: docstring-tailor\n"
        '        args: [--style, google, --line-length, "88"]\n'
    )

    _formatter = HtmlFormatter(nowrap=True, noclasses=True, style="friendly")
    _highlighted = highlight(_hook_config, YamlLexer(), _formatter)

    _hook_block = mo.Html(
        '<pre style="font-family:monospace; font-size:14px; line-height:1.4; margin:0; '
        'padding:12px 14px; border-radius:6px; background:#f6f8fa; color:#1f2328; '
        f'white-space:pre; overflow-x:auto;">{_highlighted}</pre>'
    )

    _hook_text = text_slide(
        """
    ```bash
    pre-commit install   # or: prek install
    ```

    Like the Ruff hook, it rewrites the file and stops the commit, so you can review
    and stage the change.
    """,
        font_size="17px",
    )

    _hook = mo.vstack(
        [mo.md("### Pre-commit hook").style({"font-size": "17px"}), _hook_block, _hook_text],
        gap=0.75,
    )

    mo.hstack([_commands, _hook], widths=[1, 1.2], align="start", gap=1.5)
    return


@app.cell
def _(mo):
    import math as _math

    # The expected files form a triangle; the messy input sits in the middle.
    _radius = 44
    _nodes = {60: (280, 130), 80: (120, 330), 100: (440, 330)}
    _input_centre = (280, 263)
    _line = 'stroke="#8c959f" stroke-width="2" fill="none"'

    def _shortened(start: tuple, end: tuple, cut_start: float, cut_end: float) -> tuple:
        """Returns the end points of a line between two centres, cut short at both ends."""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = _math.hypot(dx, dy)
        ux = dx / length
        uy = dy / length

        points = (
            start[0] + ux * cut_start,
            start[1] + uy * cut_start,
            end[0] - ux * cut_end,
            end[1] - uy * cut_end,
        )

        return points

    _edges = []

    # Between expected files: arrows both ways (format A at B's length gives B).
    for _a, _b in [(60, 80), (60, 100), (80, 100)]:
        _x1, _y1, _x2, _y2 = _shortened(_nodes[_a], _nodes[_b], _radius + 4, _radius + 4)
        _edges.append(
            f'<line x1="{_x1:.0f}" y1="{_y1:.0f}" x2="{_x2:.0f}" y2="{_y2:.0f}" {_line} '
            'marker-start="url(#arrow)" marker-end="url(#arrow)"/>'
        )

    # From the messy input to every expected file.
    for _target in _nodes.values():
        _x1, _y1, _x2, _y2 = _shortened(_input_centre, _target, 30, _radius + 4)
        _edges.append(
            f'<line x1="{_x1:.0f}" y1="{_y1:.0f}" x2="{_x2:.0f}" y2="{_y2:.0f}" '
            'stroke="#bc4c00" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#arrow-input)"/>'
        )

    # Self-loops: formatting an expected file at its own length leaves it unchanged.
    _loops = []

    for _length, (_x, _y) in _nodes.items():
        _direction = -1 if _length == 60 else 1
        _top = _y + _direction * (_radius - 4)
        _peak = _y + _direction * (_radius + 50)
        _label_y = _y + _direction * (_radius + 62) + (4 if _direction == 1 else 0)
        _loops.append(
            f'<path d="M {_x - 16} {_top} C {_x - 50} {_peak}, {_x + 50} {_peak}, {_x + 16} {_top}" '
            f'{_line} marker-end="url(#arrow)"/>'
            f'<text x="{_x}" y="{_label_y}" text-anchor="middle" font-size="14" fill="#59636e">unchanged</text>'
        )

    _circles = "".join(
        f'<circle cx="{_x}" cy="{_y}" r="{_radius}" fill="#dafbe1" stroke="#1a7f37" stroke-width="2"/>'
        f'<text x="{_x}" y="{_y - 4}" text-anchor="middle" font-size="24" font-weight="700" fill="#1f2328">{_length}</text>'
        f'<text x="{_x}" y="{_y + 16}" text-anchor="middle" font-size="12" fill="#59636e">expected</text>'
        for _length, (_x, _y) in _nodes.items()
    )

    _ix, _iy = _input_centre
    _input_box = (
        f'<rect x="{_ix - 58}" y="{_iy - 20}" width="116" height="40" rx="8" '
        'fill="#fff1e5" stroke="#bc4c00" stroke-width="2"/>'
        f'<text x="{_ix}" y="{_iy + 5}" text-anchor="middle" font-size="15" fill="#1f2328">messy input</text>'
    )

    _svg = (
        '<svg viewBox="0 0 560 460" width="100%" style="max-height:440px;" '
        'role="img" aria-label="Golden-file test graph">'
        "<defs>"
        '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#8c959f"/></marker>'
        '<marker id="arrow-input" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
        '<path d="M 0 0 L 10 5 L 0 10 z" fill="#bc4c00"/></marker>'
        "</defs>"
        + "".join(_edges)
        + "".join(_loops)
        + _circles
        + _input_box
        + "</svg>"
    )

    mo.Html(
        f"""
        <h2 style="margin:0 0 14px;">Lessons from building it</h2>
        <div style="display:flex; gap:28px; align-items:flex-start;">
          <div style="flex:1;">
            <h3 style="margin:0 0 4px;">Golden-file tests</h3>
            {_svg}
            <p style="font-size:16px; margin:4px 0 0;">
              Every arrow is a test: format the file at the target’s line length and
              compare it with the expected file. 238 golden-file cases, 100% line and
              branch coverage.
            </p>
          </div>
          <div style="flex:1;">
            <h3 style="margin:0 0 8px;">Tools that undo each other</h3>
            <pre style="font-size:15px; background:#f6f8fa; padding:12px; border-radius:6px; margin:0; white-space:pre; overflow:hidden;">Ruff:              \"\"\" "#rrggbb" …\"\"\"
docstring-tailor:  \"\"\""#rrggbb" …\"\"\"</pre>
            <p style="font-size:16px; margin:10px 0 0;">
              Ruff adds a space when a docstring starts with a quote; docstring-tailor
              removes it again. In a pre-commit hook, each reformats the file on every run.
              Found in another project of mine; the fix is on the list.
            </p>
          </div>
        </div>
        """
    )
    return


@app.cell
def _(text_slide):
    text_slide("""
    ## What’s next

    - Finish the Sphinx style, and add Epydoc
    - More parsing rules
    - A language server (LSP): a warning in your editor when a docstring breaks the
      parsing rules

    ## Try it

    ```bash
    uv add --dev docstring-tailor
    ```

    [github.com/AukeB/docstring-tailor](https://github.com/AukeB/docstring-tailor) ·
    [pypi.org/project/docstring-tailor](https://pypi.org/project/docstring-tailor/)
    """)
    return


@app.cell
def _(text_slide):
    text_slide("""
    # Questions?

    [github.com/AukeB/docstring-tailor](https://github.com/AukeB/docstring-tailor)
    """)
    return


if __name__ == "__main__":
    app.run()
