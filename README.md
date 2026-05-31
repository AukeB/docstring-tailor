# Docstring Tailor 🪡

Automatic formatting of Python docstrings according to PEP 257 and a predefined maximum number of chacacters per line.

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

## Docstring conventions according to PEP 257

See https://peps.python.org/pep-0257/ for the complete document.

**What is a docstring?** A docstring is a string literal that occurs as the first statement in a module, function, class, or method definition. Such a docstring becomes the `__doc__` special attribute of that object.

## Different types and forms of docstrings

The PEP document makes distinctions between different types of docstrings. For some docstring properties, the convention depends on the kind of object it belongs to. For module docstrings, it can also further depend on the type of python file. Therefore, a distinction is made between these **types** of docstrings:

**Three types of docstrings**:
1. Module docstrings
    - Module docstrings for scripts (stand-alone programs)
    - Module docstrings for `__init__.py` files
    - Module docstrings for 'normal' modules.
2. Class docstrings
3. Method or function docstrings

Besides the types, docstrings can occur in two different **forms**.

**Two forms of docstrings**:
1. One-line docstrings
2. Multi-line docstrings

### Conventions for one-line docstrings
1. Triple quotes are used even though the string fits on one line. This makes it easy to later expand it.
2. The closing quotes are on the same line as the opening quotes. This looks better for one-liners.
3. There’s no blank line either before or after the docstring, except when the the type of docstring is a class docstring. Then there should be a blank line after the docstring.
4. The docstring is a phrase ending in a period. It prescribes the function or method’s effect as a command (“Do this”, “Return that”), not as a description; e.g. don’t write “Returns the pathname …”.
5. The one-line docstring should NOT be a “signature” reiterating the function/method parameters (which can be obtained by introspection).

### Conventions for multi-line docstrings
1. Multi-line docstrings consist of a summary line just like a one-line docstring, followed by a blank line, followed by a more elaborate description. The summary line may be used by automatic indexing tools; it is important that it fits on one line and is separated from the rest of the docstring by a blank line.
2. The summary line may be on the same line as the opening quotes or on the next line.
3. The entire docstring is indented the same as the quotes at its first line.
4. Insert a blank line after all docstrings (one-line or multi-line) that document a class.
5. Blank lines should be removed from the beginning and end of the docstring.

#### Module docstrings

5. The docstring for a module should generally list the classes, exceptions and functions (and any other objects) that are exported by the module, with a one-line summary of each. (These summaries generally give less detail than the summary line in the object’s docstring.) 
6. The docstring of a script (a stand-alone program) should be usable as its “usage” message, printed when the script is invoked with incorrect or missing arguments (or perhaps with a “-h” option, for “help”)
7. The docstring for a package (i.e., the docstring of the package’s `__init__.py` module) should also list the modules and subpackages exported by the package.

#### Function or method docstrings

8. The docstring for a function or method should summarize its behavior and document its arguments, return value(s), side effects, exceptions raised, and restrictions on when it can be called (all if applicable). Optional arguments should be indicated. It should be documented whether keyword arguments are part of the interface.

#### Class docstrings

9. The docstring for a class should summarize its behavior and list the public methods and instance variables. If the class is intended to be subclassed, and has an additional interface for subclasses, this interface should be listed separately (in the docstring). The class constructor should be documented in the docstring for its __init__ method. Individual methods should be documented by their own docstring.
10. If a class subclasses another class and its behavior is mostly inherited from that class, its docstring should mention this and summarize the differences.

## Formatting operations applied by this tool

**How does this tool detect docstrings?**: All string literals that start with triple double quotes (""") are recognized as docstrings and will potentially be formatted.

**One-line docstrings**
- Regarding the 5 conventions mentioned above for one-line docstrings, only convention number 2 is enforced (The closing quotes are on the same line as the opening quotes).
- It is the user's reponsibility to adhere to convention number 1, since the triple quotes are used by this tool to detect the docstring. The same goes for convention number 3, 4 and 5.

- Besides the conventions mentioned above, the docstring is formatted according to a pre-defined maximum number of characters per line (**line length**). This means:
    - If a docstring is spread out over multiple lines, but it could fit on one line, it will be converted to a one-line docstring.
    - If a docstring exceeds the line length, it will be converted to a multi-line docstring.

**Multi-line docstrings**
- Regarding the conventions for multi-line docstrings mentioned above, number 2 is applied. This means if the summary line is on the next line, it will be enforced on the same line as the opening triple double quotes.
- Convention number 5 is also enforced, blank lines at the start and end of the docstring are removed.
- Most of the other conventions are about the content of the docstring, which are not checked by this tool.

Next to that, the layout of the docstring is preserved. For now the focus is on the 'Google' type docstring format, which in its most basic form, looks like this.

```
def function_with_pep484_type_annotations(param1: int, param2: str) -> bool:
    """Example function with PEP 484 type annotations.

    Args:
        param1: The first parameter.
        param2: The second parameter.

    Returns:
        The return value. True for success, False otherwise.
    """
```

Or it can look like this:

```
def example_generator(n):
    """Generators have a ``Yields`` section instead of a ``Returns`` section.

    Args:
        n (int): The upper limit of the range to generate, from 0 to `n` - 1.

    Yields:
        int: The next number in the range of 0 to `n` - 1.

    Examples:
        Examples should be written in doctest format, and should illustrate how
        to use the function.

        >>> print([i for i in example_generator(4)])
        [0, 1, 2, 3]

    """
    for i in range(n):
        yield i
```

Maintaining this structure, while enforcing a maximum characters per line, means the following rules have to be implented in the formatting logic.

- If the user starts a new line, even though there is still space on the current line for the next word, it should be corrected and the word should be moved to the current line.
- If the line is too long, the part that exceeds the line limit should be moved to the next line.
- If the user uses two `\n` characters, it means this was a deliberate choice (for example, starting the 'Args' section) and this should be preserved.
- Single `\n` characters, in for example the 'Args' section should be preserved, as each parameter should start on a new line.
- If the docstring contains an 'Example' or 'Examples' section, the indentation for the code part and the code itself (indicated with `>>>` and `...`) should be untouched, as this code should be able to be interpreted.