"""Utility for translating structured list and named paragraph keywords between
docstring styles.

Parsing and rendering alone are not enough to convert a docstring from one style
to another: Google's 'Args' and NumPy's 'Parameters' describe the same concept
but are different literal strings, and StructuredList.keyword /
NamedParagraph.header always hold whatever literal string the source style used.
Converting between styles therefore requires an extra step, applied to the IR
between parsing and rendering, that rewrites these keywords into the target
style's vocabulary.

TODO: implemented here as two flat per-direction dicts, which is fine for two
styles but scales quadratically as Sphinx and Epydoc are added. Once a third
style arrives, consider refactoring to a canonical concept per section (e.g. an
enum: PARAMETERS, RETURNS, RAISES, ...) with one keyword-per- style lookup table
each, so adding a style only adds one table instead of one per existing style.
"""

from docstring_tailor.cli_config import DocstringStyle
from docstring_tailor.ir_model import DocstringNode, NamedParagraph, StructuredList

# Canonical keyword literals, defined once to avoid repeating the same strings
# across the many per-direction translation tables below.
_ARGS = "Args"
_PARAMETERS = "Parameters"
_ATTRIBUTES = "Attributes"
_RETURNS = "Returns"
_YIELDS = "Yields"
_RAISES = "Raises"
_RECEIVES = "Receives"
_METHODS = "Methods"
_NOTE = "Note"
_NOTES = "Notes"
_WARNING = "Warning"
_WARNINGS = "Warnings"
_EXAMPLE = "Example"
_EXAMPLES = "Examples"
_REFERENCES = "References"
_SEE_ALSO = "See Also"

# Google keywords with no NumPy equivalent in NUMPY_PLAIN_SECTIONS are kept
# as-is, so content is never dropped -- though the result won't be recognized
# as a structured NumPy keyword if it is parsed again.
GOOGLE_TO_NUMPY_KEYWORDS: dict[str, str] = {
    _ARGS: _PARAMETERS,
    "Arguments": _PARAMETERS,
    _ATTRIBUTES: _ATTRIBUTES,
    _RETURNS: _RETURNS,
    _YIELDS: _YIELDS,
    _RAISES: _RAISES,
    _NOTE: _NOTES,
    _NOTES: _NOTES,
    _EXAMPLE: _EXAMPLES,
    _EXAMPLES: _EXAMPLES,
    _REFERENCES: _REFERENCES,
    _SEE_ALSO: _SEE_ALSO,
    _WARNING: _WARNING,
    _WARNINGS: _WARNINGS,
}

# NumPy keywords with no Google equivalent (Receives, Methods) are kept as-is
# for the same reason.
NUMPY_TO_GOOGLE_KEYWORDS: dict[str, str] = {
    _PARAMETERS: _ARGS,
    _ATTRIBUTES: _ATTRIBUTES,
    _RETURNS: _RETURNS,
    _YIELDS: _YIELDS,
    _RAISES: _RAISES,
    _RECEIVES: _RECEIVES,
    _METHODS: _METHODS,
    _EXAMPLES: _EXAMPLES,
    _NOTES: _NOTES,
    _REFERENCES: _REFERENCES,
    _SEE_ALSO: _SEE_ALSO,
}

# Sphinx StructuredList/NamedParagraph keywords use the canonical spellings
# 'Parameters', 'Returns', 'Raises' (structured) and 'Note', 'Warning', 'See
# Also', 'Example' (admonitions). Keywords with no target-style equivalent are
# kept as-is so content is never dropped.
SPHINX_TO_GOOGLE_KEYWORDS: dict[str, str] = {
    _PARAMETERS: _ARGS,
    _RETURNS: _RETURNS,
    _RAISES: _RAISES,
    _NOTE: _NOTE,
    _WARNING: _WARNING,
    _SEE_ALSO: _SEE_ALSO,
    _EXAMPLE: _EXAMPLE,
}

GOOGLE_TO_SPHINX_KEYWORDS: dict[str, str] = {
    _ARGS: _PARAMETERS,
    "Arguments": _PARAMETERS,
    _ATTRIBUTES: _PARAMETERS,
    _RETURNS: _RETURNS,
    _YIELDS: _RETURNS,
    _RAISES: _RAISES,
    _NOTE: _NOTE,
    _NOTES: _NOTE,
    _WARNING: _WARNING,
    _WARNINGS: _WARNING,
    _SEE_ALSO: _SEE_ALSO,
    _EXAMPLE: _EXAMPLE,
    _EXAMPLES: _EXAMPLE,
    _REFERENCES: _REFERENCES,
}

SPHINX_TO_NUMPY_KEYWORDS: dict[str, str] = {
    _PARAMETERS: _PARAMETERS,
    _RETURNS: _RETURNS,
    _RAISES: _RAISES,
    _NOTE: _NOTES,
    _WARNING: _WARNING,
    _SEE_ALSO: _SEE_ALSO,
    _EXAMPLE: _EXAMPLES,
}

NUMPY_TO_SPHINX_KEYWORDS: dict[str, str] = {
    _PARAMETERS: _PARAMETERS,
    _ATTRIBUTES: _PARAMETERS,
    _RETURNS: _RETURNS,
    _YIELDS: _RETURNS,
    _RAISES: _RAISES,
    _NOTES: _NOTE,
    _EXAMPLES: _EXAMPLE,
    _REFERENCES: _REFERENCES,
    _SEE_ALSO: _SEE_ALSO,
}


def _get_translation_table(
    from_style: DocstringStyle, to_style: DocstringStyle
) -> dict[str, str]:
    """Looks up the keyword translation table for a style pair.

    Args:
        from_style (DocstringStyle): The source style.
        to_style (DocstringStyle): The target style.

    Returns:
        table (dict[str, str]): Maps from_style keywords to to_style keywords.

    Raises:
        ValueError: If no translation table exists for the given style pair.
    """
    tables: dict[tuple[DocstringStyle, DocstringStyle], dict[str, str]] = {
        (DocstringStyle.google, DocstringStyle.numpy): GOOGLE_TO_NUMPY_KEYWORDS,
        (DocstringStyle.numpy, DocstringStyle.google): NUMPY_TO_GOOGLE_KEYWORDS,
        (DocstringStyle.sphinx, DocstringStyle.google): SPHINX_TO_GOOGLE_KEYWORDS,
        (DocstringStyle.google, DocstringStyle.sphinx): GOOGLE_TO_SPHINX_KEYWORDS,
        (DocstringStyle.sphinx, DocstringStyle.numpy): SPHINX_TO_NUMPY_KEYWORDS,
        (DocstringStyle.numpy, DocstringStyle.sphinx): NUMPY_TO_SPHINX_KEYWORDS,
    }

    table = tables.get((from_style, to_style))

    if table is None:
        raise ValueError(
            f"No keyword translation available from {from_style.value!r} to "
            f"{to_style.value!r}."
        )

    return table


def translate_keywords(
    ir: list[DocstringNode], from_style: DocstringStyle, to_style: DocstringStyle
) -> list[DocstringNode]:
    """Translates StructuredList and NamedParagraph keywords from one style's
    vocabulary to another's.

    A NamedParagraph body cannot itself contain StructuredList or NamedParagraph
    nodes, so only the top-level IR list needs to be walked -- no recursion into
    node bodies is required.

    Args:
        ir (list[DocstringNode]): Parsed IR, with keywords still in from_style's
            vocabulary.
        from_style (DocstringStyle): The style the IR was parsed from.
        to_style (DocstringStyle): The style the IR will be rendered to.

    Returns:
        translated_ir (list[DocstringNode]): A new IR list with keywords
            translated to to_style's vocabulary. Nodes that carry no keyword
            (Paragraph, CodeBlock, CodeREPL, SimpleList) pass through unchanged.

    Raises:
        ValueError: If from_style and to_style are not a supported translation
            pair.
    """
    translation_table = _get_translation_table(from_style, to_style)
    translated_ir: list[DocstringNode] = []

    for node in ir:
        if isinstance(node, StructuredList):
            translated_keyword = translation_table.get(node.keyword, node.keyword)
            translated_ir.append(
                StructuredList(keyword=translated_keyword, entries=node.entries)
            )
        elif isinstance(node, NamedParagraph):
            translated_header = translation_table.get(node.header, node.header)
            translated_ir.append(
                NamedParagraph(header=translated_header, body=node.body)
            )
        else:
            translated_ir.append(node)

    return translated_ir
