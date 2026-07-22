# Docstring Tailor 🪡

Formats Python docstrings to PEP 257 style with configurable line length.

[![PyPI Version](https://img.shields.io/pypi/v/docstring-tailor?color=lightblue)](https://pypi.org/project/docstring-tailor/)
[![License](https://img.shields.io/pypi/l/docstring-tailor?color=lightblue)](https://pypi.org/project/docstring-tailor/)
[![Wheel](https://img.shields.io/pypi/wheel/docstring-tailor?color=lightblue)](https://pypi.org/project/docstring-tailor/)
[![Downloads](https://img.shields.io/pypi/dm/docstring-tailor?color=lightblue)](https://pypi.org/project/docstring-tailor/)


## Table of Contents
1. [Demo](#demo)
2. [Installation](#Installation)
3. [Quick start](#quick_start)
4. [API Overview](#api-overview)
    - [Command](#command)
    - [Options](#options)
    - [Examples](#examples)
5. [Example docstrings](#example-docstrings)
6. [What Your Line Length Says About You!](#what-your-line-length-says-about-you)
7. [Resources](#resources)
8. [Release Notes](#release_notes)
9. [Roadmap](#roadmap)

## Demo

<details>
<summary><b>Show demo</b></summary>

<br>

- `docstring-tailor` formats docstrings to fit a given line length, while preserving its structure throughout — For exapmle blank lines, argument indentation, continuation line alignment, and code blocks in the Examples section all remain intact.
- **Note**: The slider in the [Marimo notebook](https://marimo.io/) is not part of the package. It was created solely to illustrate how the output changes continuously as the line length varies.

<br>

<img src="https://github.com/user-attachments/assets/983ae257-472d-465e-9924-9d90bca10f0d" alt="" />
<img src="https://i.imgur.com/2uG5HNh.gif" alt="" />

If the image does not show, click [here](https://github.com/user-attachments/assets/983ae257-472d-465e-9924-9d90bca10f0d).

</details>

## Installation

Installation with [UV](https://docs.astral.sh/uv/) (recommended)
```bash
uv add --dev docstring-tailor
```

Or with pip:

```bash
pip install docstring-tailor
```

## Quick start

Run on a single file or directory:

```bash
uv run docstring_tailor format my_file.py
uv run docstring_tailor format my_folder
```
Multiple files and/or folders are also accepted. Without a file path or folder path, it will try to locate the `src` folder.

The default line length is 100. To customise it:

```bash
uv run docstring_tailor format --line-length 88
```

Configure it permanently in `pyproject.toml` or in `docstring_tailor.toml`:

```toml
# pyproject.toml
[tool.docstring_tailor]
line-length = 88
```

```toml
# docstring_tailor.toml
line-length = 88
```

Define a docstring style. Two styles are currently supported: [Google](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) and [NumPy](https://numpydoc.readthedocs.io/en/latest/format.html). Google is the default. Explicit configuration:

```bash
uv run docstring_tailor format --style numpy
```

or in `pyproject.toml`

```toml
[tool.docstring_tailor]
style = "google"
```

To convert existing docstrings from one style to another, use the `convert` command instead:

```bash
uv run docstring_tailor convert my_file.py --from-style google --to-style numpy
```

## API Overview

### Commands

`docstring_tailor` has two commands: `format` and `convert`.

**`format`** reformats docstrings in place, in a single style — use this for everyday formatting (adjusting line length, wrapping, whitespace) without changing the docstring style itself.

**`convert`** reparses and re-renders docstrings from one style into another — use this the one time you need to migrate a codebase, or part of one, between styles.

```bash
uv run docstring_tailor format [PATHS ...] [OPTIONS]
uv run docstring_tailor convert [PATHS ...] --from-style STYLE --to-style STYLE [OPTIONS]
```
`PATHS` may contain one or more files and/or directories.
Examples:
```bash
uv run docstring_tailor format my_file.py
uv run docstring_tailor format src/
uv run docstring_tailor format src/ tests/test_file.py
uv run docstring_tailor convert src/ --from-style google --to-style numpy
```
If no paths are provided, `docstring_tailor` will attempt to locate and format files inside the `src` directory.

### Options

#### `format`

| <div style="width:140px">Option</div> | <div style="width:50px">Type</div> | <div style="width:80px">Default</div> | Description |
|---|---|---|---|
| `--line-length`      | `int`  | 100    | Maximum number of characters allowed per line after formatting. |
| `--style`            | `str`  | google | Docstring style to format to. `google` or `numpy`. |
| `--exclude`          | `str`  | —      | A glob pattern for paths to exclude. Can be passed multiple times. Single-path patterns (e.g. `tests`, `*.pyi`) match by name anywhere in the tree. Relative patterns (e.g. `src/generated/*.py`) match against the path relative to the project root. |
| `--diff`             | flag   | —      | Print a unified diff of changes to stdout instead of modifying files. No files are written when this flag is set. |

#### `convert`

| <div style="width:140px">Option</div> | <div style="width:50px">Type</div> | <div style="width:80px">Default</div> | Description |
|---|---|---|---|
| `--from-style`       | `str`  | *required* | Docstring style to convert from. `google` or `numpy`. |
| `--to-style`         | `str`  | *required* | Docstring style to convert to. `google` or `numpy`. Must differ from `--from-style`. |
| `--line-length`      | `int`  | 100    | Maximum number of characters allowed per line after formatting. |
| `--exclude`          | `str`  | —      | A glob pattern for paths to exclude. Can be passed multiple times. Single-path patterns (e.g. `tests`, `*.pyi`) match by name anywhere in the tree. Relative patterns (e.g. `src/generated/*.py`) match against the path relative to the project root. |
| `--diff`             | flag   | —      | Print a unified diff of changes to stdout instead of modifying files. No files are written when this flag is set. |

`--from-style` and `--to-style` have no config-file or default fallback — both must be given explicitly on every `convert` invocation, and must be different from each other.

#### Global

| <div style="width:140px">Option</div> | <div style="width:50px">Type</div> | <div style="width:80px">Default</div> | Description |
|---|---|---|---|
| `--version`, `-V`    | flag   | —      | Print the installed version and exit. |
| `--help`             | flag   | —      | Show the help message and exit. |

### Examples

`CLI`
```bash
uv run docstring_tailor format src/ --line-length 88
uv run docstring_tailor format my_file.py --style numpy
uv run docstring_tailor format src/ --exclude tests --exclude "src/generated/*.py"
uv run docstring_tailor format src/ --diff
uv run docstring_tailor convert src/ --from-style google --to-style numpy
uv run docstring_tailor convert my_file.py --from-style numpy --to-style google --diff
uv run docstring_tailor --version
uv run docstring_tailor --help
```
`pyproject.toml`
```toml
[tool.docstring_tailor]
line-length = 88
style = "google"
exclude = ["tests", "src/generated/*.py"]
```

`docstring_tailor.toml`
```toml
line-length = 88
style = "google"
exclude = ["tests", "src/generated/*.py"]
```

## Example docstrings

1. [Module docstring](#module-docstring)
2. [Class docstring](#class-docstring)
3. [Function docstring](#function-docstring)
4. [Codeblocks](#codeblocks)
5. [Other sections](#other-sections)
6. [Unordered and numbered lists](#unordered-and-numbered-lists)

### Module docstring

**Google / Numpy** (identical for this example)

```python
"""Demonstrates a minimal Google or Numpy style module docstring.

This module exists as a formatting example and illustrates the typical
structure of a docstring, including a concise summary line followed by 
an additional descriptive paragraph.
"""
```

- Leave a **blank line** between the summary line and the more elaborate description. This applies to both styles.

### Class docstring

**Google**

```python
class ExampleConfiguration:
    """Represents a configuration object used to demonstrate Google-
    style class docstrings.

    This class is provided as a formatting example and illustrates how
    attributes are documented consistently in the Google docstring
    style.

    Attributes:
        example_argument_1 (str): Stores the first configuration value
            provided at initialization.
        example_argument_2 (int): Stores the second configuration
            value provided at initialization.
    """
```

- The `Attributes` section is recognized by the formatter and triggers special indentation rules for attribute entries.
- If an attribute's description runs onto the next line, it **must be indented one extra level beyond the attribute name**. The formatter relies on this indentation to tell a new attribute entry apart from a continuation of the previous one.

**NumPy**

```python
class ExampleConfiguration:
    """Represents a configuration object used to demonstrate NumPy-
    style class docstrings.

    This class is provided as a formatting example and illustrates how
    attributes are documented consistently in the NumPy docstring
    style.

    Attributes
    ----------
    example_argument_1 : str
        Stores the first configuration value provided at
        initialization.
    example_argument_2 : int
        Stores the second configuration value provided at
        initialization.
    """
```

- The `Attributes` section header is followed by a line of dashes matching its length (`----------`).
- Each attribute is written as `name : type`, and its description starts on the next line. Continuation lines are indented to line up with the description, one level deeper than the `name : type` line.

### Function docstring

**Google**

```python
def example_function(example_argument_1: str, example_argument_2: int) -> str:
    """Demonstrates a Google-style function docstring with multiple
    sections.

    This function exists purely as a formatting example and
    illustrates how Args, Returns, Examples, and Raises sections are
    structured in a Google-style docstring.

    Args:
        example_argument_1 (str): First example input value used to
            construct a formatted result string.
        example_argument_2 (int): Second example input value used to
            influence the transformation logic.

    Returns:
        str: A formatted string combining both input arguments into a
            single human-readable representation.

    Examples:
        Basic usage with typical inputs produces a simple combined
        string:

        >>> example_function("alpha", 3)
        'alpha-3'

        You can also write text in between two Python REPL sections,
        and this part will be formatted, while the two small code
        sections won't be formatted.

        >>> example_function(
        ...     "beta",
        ...     7,
        ... )
        'beta-7'

    Raises:
        ValueError: Raised when example_argument_2 is negative or
            zero, as only positive integers are considered valid in
            this demonstration.
    """
    if example_argument_2 <= 0:
        raise ValueError("example_argument_2 must be positive")

    return f"{example_argument_1}-{example_argument_2}"
```

- `Args`, `Returns`, `Examples`, and `Raises` are all keywords recognized by the package.
- You can use either `Args` or `Arguments` for the argument section, and `Example` or `Examples` for the example section.
- As with the `Attributes` section above, add **one extra level of indentation** for the description of an argument, return value, or error, whenever it spans multiple lines.
- In the `Example(s)` section, start the Python REPL with `>>>` and use `...` for continuation lines, matching Pydoc conventions.
- These same keywords can also be used in module or class docstrings — for example, an `Args` section in a class docstring, or an `Example(s)` section in a module docstring.

**NumPy**

```python
def example_function(example_argument_1: str, example_argument_2: int) -> str:
    """Demonstrates a NumPy-style function docstring with multiple
    sections.

    This function exists purely as a formatting example and
    illustrates how Parameters, Returns, Examples, and Raises sections
    are structured in a NumPy-style docstring.

    Parameters
    ----------
    example_argument_1 : str
        First example input value used to construct a formatted
        result string.
    example_argument_2 : int
        Second example input value used to influence the
        transformation logic.

    Returns
    -------
    str
        A formatted string combining both input arguments into a
        single human-readable representation.

    Examples
    --------
    Basic usage with typical inputs produces a simple combined string:

    >>> example_function("alpha", 3)
    'alpha-3'

    You can also write text in between two Python REPL sections, and
    this part will be formatted, while the two small code sections
    won't be formatted.

    >>> example_function(
    ...     "beta",
    ...     7,
    ... )
    'beta-7'

    Raises
    ------
    ValueError
        Raised when example_argument_2 is negative or zero, as only
        positive integers are considered valid in this demonstration.
    """
    if example_argument_2 <= 0:
        raise ValueError("example_argument_2 must be positive")

    return f"{example_argument_1}-{example_argument_2}"
```

- `Parameters`, `Returns`, `Examples`, and `Raises` are all keywords recognized by the package. Each is followed by an underline of dashes matching the header's length.
- Parameters and return values are documented as `name : type` (or just `type` for a return value), with the description indented on the following line(s).
- As with the `Attributes` section above, add **one extra level of indentation** for a description that spans multiple lines, so it lines up under the `name : type` entry rather than under the header.
- In the `Examples` section, start the Python REPL with `>>>` and use `...` for continuation lines, matching Pydoc conventions — same as Google style.
- These same section keywords can also be used in module or class docstrings — for example, a `Parameters` section in a class docstring, or an `Examples` section in a module docstring.

### Codeblocks

**Google / Numpy** (identical for this example)

```python
"""Demonstrates a Google or Numpy style module docstring containing 
a code block.
 
This module-level docstring is used as a formatting example and shows
how code blocks can be embedded inside docstrings using fenced
delimiters.
 
~~~
def example_function(x, y):
    return x + y
~~~
```

- A code block can appear inside the `Example(s)` section, but it doesn't have to — it can also stand on its own outside of it.
- Either backticks (` ``` `) or tildes (`~~~`) can be used to fence the block, the same way code blocks work in markdown files. This is true for both styles.

### Other sections

**Google — Yields**

```python
def example_generator(n):
    """Generators have a ``Yields`` section instead of a ``Returns``
    section.

    Args:
        n (int): The upper limit of the range to generate, from 0 to
            `n` - 1.

    Yields:
        int: The next number in the range of 0 to `n` - 1.
    """
```

**NumPy — Yields**

```python
def example_generator(n):
    """Generators have a ``Yields`` section instead of a ``Returns``
    section.

    Parameters
    ----------
    n : int
        The upper limit of the range to generate, from 0 to `n` - 1.

    Yields
    ------
    int
        The next number in the range of 0 to `n` - 1.
    """
```

- `Yields` is supported as a drop-in replacement for `Returns` in both styles, for use in generator functions.

**Google — Note**

```python
"""Demonstrates a Google-style module docstring containing a Note
section.

This module-level docstring is used as a formatting example and
illustrates how additional informational sections can be included
alongside the main description in a Google-style docstring.

Note:
    The formatting of this docstring is intentionally designed to test
    how note sections are detected and preserved during docstring
    transformation.
"""
```

- `Note` is a supported keyword; you can use either `Note` or `Notes`.

**NumPy — Notes**

```python
"""Demonstrates a NumPy-style module docstring containing a Notes
section.

This module-level docstring is used as a formatting example and
illustrates how additional informational sections can be included
alongside the main description in a NumPy-style docstring.

Notes
-----
The formatting of this docstring is intentionally designed to test how
notes sections are detected and preserved during docstring
transformation.
"""
```

- `Notes` is the conventional NumPy keyword for this section (as opposed to `Note`, which is the singular form used in Google style).

### Unordered and numbered lists

The following examples are valid for **both Google and NumPy** styles, since list formatting isn't tied to a particular section keyword.

```python
"""Demonstrates that docstrings can include structured lists.

This module-level docstring is used as a formatting example and shows
how unordered lists can be represented inside a docstring. Each list
item is recognized by the formatter and rendered on a separate line.

Items:
- Demonstrates that docstrings may contain structured unordered lists
  that are parsed and formatted consistently by the docstring
  formatter.
- Shows that each list item is treated as an independent element and
  is wrapped separately when exceeding the configured line length.
- Illustrates that long list items may span multiple lines while
  preserving indentation and list structure integrity across
  formatting operations.
"""
```

```python
"""Demonstrates that docstrings can include structured lists.

This module-level docstring is used as a formatting example and shows
how numbered lists can be represented inside a docstring. Each list
item is recognized by the formatter and rendered on a separate line.

Steps:
1. Demonstrates that docstrings may contain structured numbered lists
   that are parsed and formatted consistently by the docstring
   formatter.
2. Shows that each list item is treated as a separate logical element
   and is wrapped independently when exceeding the configured line
   length.
3. Illustrates that long list items may span multiple lines while
   preserving indentation and list structure integrity across
   formatting operations.
"""
```

- Unordered and numbered lists can be a nice addition to a docstring from time to time. As with the sections above, **indentation** is what the formatter uses to detect where a new list item begins.

## What Your `line-length` says about You!

### 60 characters per line — The Minimalist Monk 🧘

You believe every character has a purpose and every extra column is a personal failure 😤. You keep your docstrings short, your functions tiny, and your emotional attachment to whitespace surprisingly strong. Variable names? Anything longer than two characters is wasteful bloat — x, y, z, and i are sufficient for any problem. Docstrings are memory theft; everything the code needs to say should be obvious from context or inferred through pure spiritual understanding 🙏. Why document when you could just make the code so minimalist that it transcends the need for explanation? Your motto: if it takes more than 60 characters to explain, the explanation itself is the bug, not the code.

### 79 characters per line — The Precision Tuner ⚙️

You didn't choose 79 characters; you derived it through first principles and a spreadsheet. You read every formatter's GitHub issues, every style guide's rationale, and you have strong opinions about why 80 is overrated but 78 is cowardice 😤. You've A/B tested readability on three different monitors, measured your own eye-tracking data, and lost sleep over whether \n counts toward the limit or not. You configure your linter to lint your linter, and you have a .editorconfig file that is longer than most people's actual code 📋. You know exactly why PEP 8 suggested 79 and you've defended this choice at dinner parties with the fervor of someone protecting their firstborn child 🛡️. You don't just use docstring_tailor; you've benchmarked it against seven alternatives and created a spreadsheet ranking their consistency. Your line length is not a preference—it's a thesis 📊. You sleep well knowing that you have optimized, and the universe is in perfect order, exactly 79 characters wide.

### 80 characters per line — The Digital Archaeologist 🦖

You have been programming for at least half a century, and you still remember when computers were mysterious machines instead of fancy boxes running websites. You believe software peaked before color displays, and honestly, you are a little disappointed with where things went 😔. You know that everything after assembly was already too high-level and a mistake, because real programming means understanding the machine, not asking some framework to do the work for you. You hate GenAI because you believe thinking is the programmer's job. Python? Far too comfortable. Your motto is simple: real programmers toggle individual transistors. Everything after that is just frameworks ⚙️.

### 88 characters per line — The Black Ritualist 🖤

You are nostalgic for the comforting embrace of Black, where every formatting decision has already been made for you. You don't want to risk the chaos of choosing your own line length because what if you accidentally become different? 😨 You trust the collective wisdom of the formatter, the community, and the thousands of developers who came before you. You are not afraid of change exactly; you are just very comfortable knowing that Black has already decided your fate. Peace through formatting consistency ✨.

### 100 characters per line — The Peacekeeper 🤝

You chose 100 characters because you wanted everyone to be happy, including the people who review your code and the people who have to read it on a laptop. You looked at 80 characters and thought it felt a little cramped, but you looked at 120 and felt society was moving too fast 😅. You carefully live in the middle, avoiding formatting wars and unnecessary debates. Nobody writes angry comments about your line length, nobody praises it either, and that quiet neutrality is exactly the comfortable existence you wanted.

### 240 characters per line — The Ultrawide Warrior 🖥️

You claim you increased your line length because it improves readability, but everyone knows the real reason: you want people to notice your enormous ultrawide monitor. You paid for every pixel, and you refuse to leave any of them unemployed 😎. Your docstrings stretch from one side of the screen to the other just to prove your setup is bigger than everyone else's. Whenever someone questions your line length, you casually mention your monitor resolution, refresh rate, and somehow the GPU model.

### 500 characters per line — The Horizon Programmer 🌌

You don't wrap text because wrapping is a skill issue. You let photons travel uninterrupted across the entire display because your docstrings deserve the full cinematic experience 🎬. You combine programming with neck exercises, allowing you to safely skip neck day at the gym. You don't use a monitor anymore; you rent a cinema, sit in the back row, and program using a telescope pointed at your code 🔭. Your Git diffs require geological surveys, satellite mapping, and a team of explorers. NASA can read your docstrings from orbit 🚀.

## Resources

### Core resources

| <div style="width:70px">Resource</div> | <div style="width:100px">Description</div> | <div style="width:130px">Link</div>
|---|---|---|
| PEP 257 - Docstring Conventions | Documents the semantics and conventions associated with Python docstrings. | [Link](https://peps.python.org/pep-0257/) |
| Google Python Style Guide | Lists *dos and don'ts* for Python programs. | [Link](https://google.github.io/styleguide/pyguide.html#s3.8-comments-and-docstrings) |
| Numpy Style Guide | Describes the syntax and best practices for docstrings used with the numpydoc extension for Sphinx | [Link](https://numpydoc.readthedocs.io/en/latest/format.html) |
| Types of indentation | Wikipedia article that defines different kinds of indentation | [Link](https://en.wikipedia.org/wiki/Indentation_(typesetting)) |

### Additional resources

| <div style="width:70px">Resource</div> | <div style="width:100px">Description</div> | <div style="width:130px">Link</div>
|---|---|---|
| PEP 8 - Style Guide for Python Code | Gives coding conventions for the Python code comprising the standard library in the main Python distribution. | [Link](https://peps.python.org/pep-0008/) |


## Release Notes

| <div style="width:70px">Version</div> | <div style="width:100px">Release date</div> | <div style="width:130px">Type</div> | Details |
|---|---|---|---|
| `0.1.0` | 2026-05-31 | Initial release | First public release of `docstring-tailor`. Includes <ul><li>Automatic docstring wrapping for module, class and function docstrings, for both one line and multi line docstrings, with a configurable `line-length` parameter.</li><li>Paragraph-aware formatting, differentiating between 'Args', 'Examples' or normal text sections.</li> <li> Docstring support for the Google `style` (Numpy, Sphinx, Epydoc not yet supported). </li><li>TOML-based configuration support.</li><li> Test coverage: 52% </ul> |
| `0.1.1` | 2026-05-31 | Documentation update | Updated the `README.md` file with the 'Installation' and 'Quick Start' section. |
| `0.2.0` | 2026-06-07 | Feature update | <ul><li>Implemented the `detect-lists` parameter, adding support for unordered and ordered (numbered) lists in docstrings. When enabled, list structures are detected automatically and each list item is formatted onto its own line.</li><li>Introduced a declarative golden-file test framework for formatter validation. Test cases are now generated from parametrized templates using Cartesian-product expansion, significantly reducing boilerplate and improving scalability for configuration coverage.</li><li>Expanded this `README.md` with the 'API Overview', 'Release Notes', 'Example docstrings' and 'Roadmap' sections.</li><li>Test coverage: 75%</li></ul> |
| `0.2.1` | 2026-06-11 | Feature update | <ul><li>Added the `-V`/`--version` command to the CLI.</li><li>Added the `--exclude` command to the CLI.</li><li>Added the `--diff` command to the CLI.</li><li>Added the 'Demo' part to to the `README.md`.</ul> |
| `0.3.0` | 2026-07-20 | Feature update & bug fixes | <ul><li>Introduced a style-agnostic intermediate representation (IR) model and refactored parsing into an abstract base class hierarchy. Google and NumPy docstrings now parse into the same IR via `IndentationBasedParser` subclasses, enabling lossless conversion between styles. Structured list parsing is delegated to style-specific implementations to handle syntactic differences (Google's inline `name (type):` vs. NumPy's `name : type` on separate lines).</li><li>Refactored rendering to match the parser architecture: `DocstringRendererBase` (ABC) with style-specific subclasses that implement two hooks — section header formatting (Google's `Args:` vs. NumPy's `Parameters` + underline) and section body indentation rules (confirmed against numpy's own docstrings to keep bodies flush with headers, unlike Google). Keyword translation between styles happens automatically during conversion.</li><li>Code sections and Python REPL blocks now also can be created outside the 'Example(s)' section.</li><li>Fixed a bug when codeblock sections contain blank lines.</li><li>Fixed a bug when the docstring starts immediately with an (un)ordered list.</li><li>Removed `detect-lists` as CLI parameter, because the logic should always be applied if the docstring contains (un)ordered lists.</li><li>Changed behaviour for empty docstrings so that it consistent with Ruff.</li></ul> |
| `0.3.1` | 2026-07-21 | Small fixes | <ul><li>The `style` parameter does not have a default argument anymore, instead it always has to be configured explicitly by the user.</li><li>Fixed a bug where one-line docstrings inside indented scopes (e.g. class or method bodies) were wrapped to multiple lines prematurely, due to indentation being counted twice when checking against the configured line length.</li> <li>Added an exception, consistent with Ruff, allowing a one-line docstring to exceed the configured line length by up to 3 characters when only the closing triple quotes would otherwise be pushed onto their own line. This prevents docstring_tailor and Ruff from repeatedly reformatting the same docstring back and forth when both are run as pre-commit hooks.</li></ul> |

## Roadmap

### Must have
- Parsing-time validation: the parser enforces structural rules on a docstring
  (e.g. well-formed sections, consistent indentation, correctly closed lists and
  code blocks) and rejects it if those rules aren't met. Formatting, rendering, and
  conversion must never run on a docstring that fails this check — malformed input
  should be refused at the parsing stage, not silently passed through. A dedicated
  lint/check command exposes these errors directly to the user, with clear and
  actionable messages, rather than only blocking format/convert silently.
- Parsing module for the remaining docstring formats (Sphinx, Epydoc), extending
  the existing style-agnostic intermediate representation (IR) to cover all four
  major styles.
- Formatting module for the remaining docstring formats (Sphinx, Epydoc), driven
  entirely by the same IR already used for Google and NumPy.

### Nice to have
- Make sure the package can be used as a pre-commit hook.
- LSP (Language Server Protocol) support, enabling real-time feedback on malformed
  docstrings directly in editors like VS Code, PyCharm and Neovim. Built on top of
  the validation layer and the existing parser, with `pygls` handling the protocol.
  Requires position tracking in the IR (line/column numbers per node) as a
  prerequisite, for precise diagnostics and editor highlighting.
- Make the package available as a VSCode extension.

### Maybe later
- Parameter that allows the user to format module, class and function docstrings
  independently.