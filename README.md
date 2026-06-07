# Docstring Tailor 🪡

Automatic formatting of Python docstrings according to PEP 257 and a predefined maximum number of chacacters per line.

[![PyPI Version](https://img.shields.io/pypi/v/docstring-tailor?color=lightblue)](https://pypi.org/project/docstring-tailor/)
[![License](https://img.shields.io/pypi/l/docstring-tailor)](https://pypi.org/project/docstring-tailor/)
[![Wheel](https://img.shields.io/pypi/wheel/docstring-tailor?color=lightblue)](https://pypi.org/project/docstring-tailor/)

## Table of Contents
1. [Installation](#Installation)
2. [Quick start](#quick_start)
3. [API Overview](#api-overview)
    - [Command](#command)
    - [Options](#options)
    - [Examples](#examples)
4. [Example docstrings](#example-docstrings)
5. [Release Notes](#release_notes)
6. [Roadmap](#roadmap)

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
uv run docstring_tailor my_file.py
uv run docstring_tailor my_folder
```
Multiple files and/or folders are also accepted. Without a file path or folder path, it will try to locate the `src` folder.

The default line length is 100. To customise it:

```bash
uv run docstring_tailor --line-length 88
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

Define a docstring style, however the only style that is currently supported is [Google](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html). This is also the default style. Explicit configuration:

```bash
uv run docstring_tailor --style google
```

or in `pyproject.toml`

```toml
[tool.docstring_tailor]
style = "google"
```

## API Overview

### Command

```bash
uv run docstring_tailor [PATHS ...] [OPTIONS]
```

`PATHS` may contain one or more files and/or directories.

Examples:

```bash
uv run docstring_tailor my_file.py
uv run docstring_tailor src/
uv run docstring_tailor src/ tests/test_file.py
```

If no paths are provided, `docstring_tailor` will attempt to locate and format files inside the `src` directory.

---

### Options

| <div style="width:140px">Option</div> | <div style="width:50px">Type</div> | <div style="width:80px">Default</div> | Description |
|---|---|---|---|
| `--line-length`  | `int`  | `100`      | Maximum number of characters allowed per line after formatting.                                                                       |
| `--style`        | `str`  | `"google"` | Docstring style to enforce. Currently only the Google docstring style is supported.                                                   |
| `--detect-lists` | `bool` | `true`     | Detect unordered and ordered/numbered lists anywhere in a docstring and preserve each list element on its own line during formatting. |

### Examples

`CLI`

```bash
uv run docstring_tailor src/ --line-length 88
uv run docstring_tailor my_file.py --style google
uv run docstring_tailor --detect-lists
uv run docstring_tailor --no-detect-lists
```

`pyproject.toml`

```toml
[tool.docstring_tailor]
line-length = 88
style = "google"
detect-lists = true
```

`docstring_tailor.toml`

```toml
line-length = 88
style = "google"
detect-lists = true
```

## Example docstrings

### Google

#### Module docstring

```python
"""Demonstrates a minimal Google-style module docstring.

This module exists as a formatting example and illustrates the typical
structure of a Google-style docstring, including a concise summary
line followed by an additional descriptive paragraph.
"""
```
- Make sure to you use a **blank line** in between the summary line and the more elaborate description.

#### Class docstring

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
- If the description of an attribute extends to the next line, **it must be indented one additional level beyond the attribute name**. This indentation level is important: it is used by the formatter to distinguish between a new attribute entry and a continuation of the previous attribute’s description.

#### Function docstring

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
- The `Args`, `Returns`, `Examples` and `Raises` section are all keywords recognized by the formatter.
- You can either use `Args` or `Arguments` for the argument section, and    `Example` or `Examples` for the example section.
- Similar to the `Attributes` section for the class docstring above, make sure to **introduce another level of indentation** for the description of a function argument, return variable or error description, if it extends to the next line.
- In the `Example` section, make sure to use `>>>` for the start of the Python REPL, and use `...` for continuation lines. In this way it is consistent with Pydoc.
- You can also use these keywords in module or class docstrings. For example, an `Args` section in a class docstring, or an `Example(s)` section in a module docstring.

#### Codeblocks

```python
"""Demonstrates a Google-style module docstring containing a code
block.

This module-level docstring is used as a formatting example and shows
how code blocks can be embedded inside docstrings using fenced
delimiters.

Example:
    ```
    def example_function(x, y):
        return x + y
    ```
"""
```

```python
"""Demonstrates a Google-style module docstring containing a code
block.

This module-level docstring is used as a formatting example and shows
how code blocks can be embedded inside docstrings using fenced
delimiters.

Example:
    ~~~
    def example_function(x, y):
        return x + y
    ~~~
"""
```
- Codeblocks should be under the `Example(s)` section.
- You can either use backticks ` ``` ` or tildes `~~~`, similar to how code sections work in markdown files.

#### Other sections

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
- Similar to `Returns`, `Yields` is also supported.

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
- `Note` is a keyword that is also supported.
- You can use either `Note` or `Notes`.

#### Unordered and numbered lists

```python
"""Demonstrates that Google-style docstrings can include structured
lists.

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
"""Demonstrates that Google-style docstrings can include structured
lists.

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

- Personally, Sometimes I like to use unordered and numbered lists in a docstring. Similar to what has been described before, **indentation** is used to detect new list elements. 


## Release Notes

| <div style="width:70px">Version</div> | <div style="width:100px">Release date</div> | <div style="width:130px">Type</div> | Details |
|---|---|---|---|
| `0.1.0` | 2026-05-31 | Initial release | First public release of `docstring-tailor`. Includes <ul><li>Automatic docstring wrapping for module, class and function docstring, for both one line and multi line docstrings, with a configurable `line-length` parameter.</li><li>Paragraph-aware formatting, differentiating between 'Args', 'Examples' or normal text sections.</li> <li> Docstring support for the Google `style` (Numpy, Sphinx, Epydoc not yet supported). </li><li>TOML-based configuration support.</li><li> Test coverage: 52% </ul> |
| `0.1.1` | 2026-05-31 | Documentation update | Updated the `README.md` file with the 'Installation' and 'Quick Start' section. |
| `0.2.0` | TBD | Feature update | <ul><li>Implemented the `detect-lists` parameter, adding support for unordered and ordered (numbered) lists in docstrings. When enabled, list structures are detected automatically and each list item is formatted onto its own line.</li><li>Introduced a declarative golden-file test framework for formatter validation. Test cases are now generated from parametrized templates using Cartesian-product expansion, significantly reducing boilerplate and improving scalability for configuration coverage.</li><li>Expanded this `README.md` with the 'API Overview', 'Release Notes', 'Example docstrings' and 'Roadmap' sections.</li><li>Test coverage: 75%</li></ul> |

## Roadmap

### Must have

- Support for all major docstrings styles (Google, Numpy, Sphinx, Epydoc).
- Add `diff` functionality that will show you the formatting changes before actually changing the file(s).
- Make sure the package can be used as a pre-commit hook.
- Add `exclude` parameters that allows the user to ignore specific files.
- Add `v`/`version` parameter that shows the version of the package.

### Nice to have

- Add docstring linting functionality by converting the docstring into an AST (Abstract Syntax Tree).
- Add docstring conversion functionality that allows you to change your docstring style. For example, conversion from the 'Google' docstring style to 'Numpy'. Passing the linting phase successfully would be a requirement for conversion.

### Maybe later

- Parameter that allows the user to format module, class and function docstrings independently.