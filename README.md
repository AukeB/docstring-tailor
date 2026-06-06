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
4. [Release Notes](#release_notes)

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
Multiple files and/or folders are also accepted. Without a file path or folder path, it will try to find the `src` folder.

The default line length is 100. To customise it:

```bash
uv run docstring_tailor --line-length 88
```

You can also set it permanently in your `pyproject.toml` or in `docstring_tailor.toml`:

```toml
# pyproject.toml
[tool.docstring_tailor]
line-length = 88
```

```toml
# docstring_tailor.toml
line-length = 88
```

You can also set a docstring style, however the only style that is currently supported is [Google](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html). This is also the default style. If you like to be explicit:

```bash
uv run docstring_tailor --style google
```

or in your `pyproject.toml`

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
| `--detect-lists` | `bool` | `true`    | Detect unordered and ordered/numbered lists anywhere in a docstring and preserve each list element on its own line during formatting. |

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

---

## Release Notes

| <div style="width:70px">Version</div> | <div style="width:100px">Release date</div> | <div style="width:130px">Type</div> | Details |
|---|---|---|---|
| `0.1.0` | 2026-05-31 | Initial release | First public release of `docstring-tailor`. Includes <ul><li>Automatic docstring wrapping for module, class and function docstring, for both one line and multi line docstrings, with a configurable `line-length` parameter.</li><li>Paragraph-aware formatting, differentiating between 'Args', 'Examples' or normal text sections.</li> <li> Docstring support for the Google `style` (Numpy, Sphinx, Epydoc not yet supported). </li><li>TOML-based configuration support.</li><li> Test coverage: 52% </ul> |
| `0.1.1` | 2026-05-31 | Instruction update | Update the `README.md` file with the 'Installation' and 'Quick Start' section. |
| `0.2.0` | TBD | Feature update | <ul><li>Implemented the `detect-lists` parameter, adding support for unordered and ordered (numbered) lists in docstrings. When enabled, list structures are detected automatically and each list item is formatted onto its own line.</li><li>Introduced a declarative golden-file test framework for formatter validation. Test cases are now generated from parametrized templates using Cartesian-product expansion, significantly reducing boilerplate and improving scalability for configuration coverage.</li></ul> |