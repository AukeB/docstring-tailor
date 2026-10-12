# TODO

## Bugs

The golden files under `tests/fixtures/` currently record these behaviours. When a bug is fixed, the affected golden files must be regenerated and reviewed.

1. **Code fence language tag is moved into the code block.** A fence such as ```` ```python ```` is rendered as ```` ``` ```` followed by a line containing `python` inside the block. This happens in all three styles, so the docstring's content changes, not only its formatting. Affects every fixture with a language tag, for example `sphinx/docstring_elements/code_block_multiple` and `sphinx/docstring_elements/named_paragraph_code_block`.
2. **Sphinx field tags have no closing colon.** The Sphinx renderer writes `:returns`, `:rtype` and `:raises` without the colon that reST requires, so `:returns The value…`, `:rtype list[float]` and `:raises : …` are not valid reST. Affects `sphinx/docstring_elements/structured_list`, `sphinx/docstring_elements/structured_list_malformed`, `sphinx/docstring_elements/structured_list_partial`, `sphinx/function_docstring`, and `convert/google_to_sphinx` and `convert/numpy_to_sphinx`.
3. **NumPy to Sphinx conversion writes the wrong fields.** A NumPy `Raises` entry is written as `:param ValueError:` instead of `:raises ValueError:`, and a NumPy `Yields` entry is written as a second `:returns` field. Affects `convert/numpy_to_sphinx`.
4. **Inline literals can be split across lines.** Wrapping can break an inline literal such as ``` ``.. note::`` ``` onto two lines, which changes how it renders. Affects `sphinx/function_docstring`.
