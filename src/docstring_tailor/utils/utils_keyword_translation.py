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

# Google keywords with no NumPy equivalent in NUMPY_PLAIN_SECTIONS are kept
# as-is, so content is never dropped -- though the result won't be recognized
# as a structured NumPy keyword if it is parsed again.
GOOGLE_TO_NUMPY_KEYWORDS: dict[str, str] = {
    "Args": "Parameters",
    "Arguments": "Parameters",
    "Attributes": "Attributes",
    "Returns": "Returns",
    "Yields": "Yields",
    "Raises": "Raises",
    "Note": "Notes",
    "Notes": "Notes",
    "Example": "Examples",
    "Examples": "Examples",
    "References": "References",
    "See Also": "See Also",
    "Warning": "Warning",
    "Warnings": "Warnings",
}

# NumPy keywords with no Google equivalent (Receives, Methods) are kept as-is
# for the same reason.
NUMPY_TO_GOOGLE_KEYWORDS: dict[str, str] = {
    "Parameters": "Args",
    "Attributes": "Attributes",
    "Returns": "Returns",
    "Yields": "Yields",
    "Raises": "Raises",
    "Receives": "Receives",
    "Methods": "Methods",
    "Examples": "Examples",
    "Notes": "Notes",
    "References": "References",
    "See Also": "See Also",
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
    if from_style == DocstringStyle.google and to_style == DocstringStyle.numpy:
        return GOOGLE_TO_NUMPY_KEYWORDS

    if from_style == DocstringStyle.numpy and to_style == DocstringStyle.google:
        return NUMPY_TO_GOOGLE_KEYWORDS

    raise ValueError(
        f"No keyword translation available from {from_style.value!r} to "
        f"{to_style.value!r}."
    )


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
