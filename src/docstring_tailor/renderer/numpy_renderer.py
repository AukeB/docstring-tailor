"""Contains the NumPy-style docstring renderer."""

from docstring_tailor.ir_model import StructuredListError, StructuredListParameter
from docstring_tailor.renderer.base_renderer import DocstringRendererBase
from docstring_tailor.utils.utils_formatting import format_text


class NumpyDocstringRenderer(DocstringRendererBase):
    """Renders a parsed docstring IR into the NumPy docstring format.

    Implements the three style-specific hooks required by DocstringRendererBase:
    the section header format (keyword plus a dashed underline on the following
    line), section bodies (both NamedParagraph bodies and StructuredList
    entries) staying flush with their header rather than indenting deeper
    (confirmed against numpy's own docstrings), and the structured list entry
    format ('name : type' header line, with the description indented one level
    deeper on the line below).
    """

    @property
    def _section_body_indented(self) -> bool:
        """NumPy keeps section bodies flush with the header -- both a Notes body
        and 'Parameters' entries share a column with their header; only a
        structured list entry's own description indents deeper.

        Returns:
            result (bool): Always False for NumPy.
        """
        result = False

        return result

    def _render_section_header(self, name: str) -> str:
        """Renders a NumPy-style section header: the keyword followed by a
        dashed underline of matching length, on the next line.

        Called while _relative_indent_level sits at the section's own level (not
        yet inside its body), so self._base_indent_level gives the correct
        alignment for the underline -- it must match the header's own
        indentation, which is supplied by the caller's separator rather than
        being part of this string itself.

        Args:
            name (str): The section keyword, e.g. 'Parameters'.

        Returns:
            header (str): The header string, e.g. 'Parameters\\n----------'.
        """
        underline = "-" * len(name)
        header = name + "\n" + self._base_indent_level + underline

        return header

    def _render_structured_list_entry(
        self, entry: StructuredListParameter | StructuredListError
    ) -> str:
        """Renders a single entry as a 'name : type' header line, followed by
        its description indented one level deeper on the next line.

        A StructuredListParameter without a name (Returns/Yields) renders its
        type alone as the header, with no ' : ' separator. A StructuredListError
        -- which only arises here when rendering an IR converted from a style
        that does distinguish Raises entries -- is treated the same way, using
        error_type as the header.

        Enters its own _nested_body block for the description, one level deeper
        than the entries themselves sit at (which is already one level deeper
        than the section header, entered by _render_structured_list).

        TODO: the header line itself is never wrapped, even if a long type
        annotation would exceed the wrap width. NumPy's convention keeps 'name :
        type' on one physical line, and type annotations rarely have a natural
        break point, so this is left as a known limitation rather than
        implemented speculatively.

        Args:
            entry (StructuredListParameter | StructuredListError): A single
                parsed entry.

        Returns:
            rendered (str): The wrapped, indented entry string, header and
                description together.
        """
        if isinstance(entry, StructuredListParameter):
            header = (
                f"{entry.name} : {entry.type}" if entry.name is not None else entry.type
            )
        else:
            header = entry.error_type

        with self._nested_body():
            description = format_text(
                text=entry.description,
                wrap_width=self._wrap_width,
                line_separator=self._line_separator,
            )
            rendered = header + self._line_separator + description

        return rendered
