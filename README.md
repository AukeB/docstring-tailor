# Docstring Tailor 🪡

Automatic formatting of Python docstrings according to PEP 257 and a predefined maximum number of chacacters per line.

## Docstring conventions according to PEP 257

See https://peps.python.org/pep-0257/ for the complete document.

**What is a docstring?** A docstring is a string literal that occurs as the first statement in a module, function, class, or method definition. Such a docstring becomes the `__doc__` special attribute of that object.

For some docstring properties, the convention depends on the kind of object it belongs to. Therefore, a distinction is made between these **types** of docstrings:

**Four types of docstrings**:
1. Module docstrings
2. Class docstrings
3. Method docstrings
4. Function docstrings

Besides the types, docstrings can occur in two different **forms**.

**Two forms of docstrings**:
1. One-line docstrings
2. Multi-line docstrings

**Conventions for one-line docstrings**:
1. Triple quotes are used even though the string fits on one line. This makes it easy to later expand it.
2. The closing quotes are on the same line as the opening quotes. This looks better for one-liners.
3. There’s no blank line either before or after the docstring, except when the the type of docstring is a class docstring. Then there should be a blank line after the docstring.
4. The docstring is a phrase ending in a period. It prescribes the function or method’s effect as a command (“Do this”, “Return that”), not as a description; e.g. don’t write “Returns the pathname …”.
5. The one-line docstring should NOT be a “signature” reiterating the function/method parameters (which can be obtained by introspection).

**Conventions for multi-line docstrings**
1. Multi-line docstrings consist of a summary line just like a one-line docstring, followed by a blank line, followed by a more elaborate description. The summary line may be used by automatic indexing tools; it is important that it fits on one line and is separated from the rest of the docstring by a blank line.
2. The summary line may be on the same line as the opening quotes or on the next line.
3. The entire docstring is indented the same as the quotes at its first line.
4. Insert a blank line after all docstrings (one-line or multi-line) that document a class.


## Formatting operations applied by this tool

**How does this tool detect docstrings?**: All string literals that start with triple double quotes (""") are recognized as docstrings and will potentially be formatted.

**One-line docstrings**
- Regarding the 5 conventions mentioned above for one-line docstrings, only convention number 2 is enforced (The closing quotes are on the same line as the opening quotes).
- It is the user's reponsibility to adhere to convention number 1, since the triple quotes are used by this tool to detect the docstring. The same goes for convention number 3, 4 and 5.

- Besides the conventions mentioned above, the docstring is formatted according to a pre-defined maximum number of characters per line (**line length**). This means:
    - If a docstring is spread out over multiple lines, but it could fit on one line, it will be converted to a one-line docstring.
    - If a docstring exceeds the line length, it will be converted to a multi-line docstring.

**Multi-line docstrings**
- f