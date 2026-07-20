"""Contains the Google-style docstring renderer."""

from docstring_tailor.ir_model import StructuredListError, StructuredListParameter
from docstring_tailor.renderer.base_renderer import DocstringRendererBase
from docstring_tailor.utils.utils_formatting import format_text


class GoogleDocstringRenderer(DocstringRendererBase):
    """Renders a parsed docstring IR into the Google docstring format.

    Implements the three style-specific hooks required by DocstringRendererBase:
    the section header format ('Args:'), the structured list entry format ('name
    (type): description'), and section bodies (both NamedParagraph bodies and
    StructuredList entries) indenting one level deeper than their header.
    """

    @property
    def _section_body_indented(self) -> bool:
        """Google indents section bodies one level deeper than the header.

        Returns:
            result (bool): Always True for Google.
        """
        result = True

        return result

    def _render_section_header(self, name: str) -> str:
        """Renders a Google-style section header: the keyword followed by a
        colon, on one line.

        Args:
            name (str): The section keyword or header text, e.g. 'Args'.

        Returns:
            header (str): The header string, e.g. 'Args:'.
        """
        header = f"{name}:"

        return header

    def _render_structured_list_entry(
        self, entry: StructuredListParameter | StructuredListError
    ) -> str:
        """Renders a single entry as "name (type): description", or "type:
        description" when the entry has no name -- the conventional shape for
        Returns/Yields entries, and coincidentally also the correct shape for a
        StructuredListError, whose error_type plays the same role as an unnamed
        type.

        Rendered as a single flowing block via format_text, wrapping with a
        hanging indent of one indent unit for any continuation lines.

        Args:
            entry (StructuredListParameter | StructuredListError): A single
                parsed entry.

        Returns:
            rendered (str): The wrapped, indented entry string.
        """
        if isinstance(entry, StructuredListParameter):
            item_text = (
                f"{entry.name} ({entry.type}): {entry.description}"
                if entry.name is not None
                else f"{entry.type}: {entry.description}"
            )
        else:
            item_text = f"{entry.error_type}: {entry.description}"

        rendered = format_text(
            text=item_text,
            wrap_width=self._wrap_width,
            line_separator=self._line_separator,
            subsequent_indent=self._indent_unit,
        )

        return rendered
