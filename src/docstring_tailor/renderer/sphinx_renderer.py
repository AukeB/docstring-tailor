"""Contains the Sphinx/reST-style docstring renderer.

Sphinx renders documented parameters, returns, and raised exceptions as a flat
reST field list rather than an indented, heading-led section, and renders
admonitions ('Note', 'Warning', ...) as '.. directive::' blocks. That physical
structure differs enough from Google's and NumPy's heading-plus-body shape that
this renderer overrides _render_structured_list and _render_named_paragraph
outright, rather than only supplying the small header/entry hooks the other two
styles share. Everything else -- paragraph wrapping, code blocks, simple lists,
one-line handling, node dispatch -- is inherited unchanged from
DocstringRendererBase.

Type output follows Style A: a parameter's type is emitted on its own ':type
name:' line and a return's type on an ':rtype:' line. When a type is absent
(None in the IR), the corresponding ':type'/':rtype' line is omitted entirely
rather than fabricated, consistent with types being optional in reST.
"""

from docstring_tailor.constants import (
    SPHINX_HEADER_DIRECTIVES,
    SPHINX_KEYWORD_RETURNS,
    SPHINX_RENDER_PARAM_TAG,
    SPHINX_RENDER_RAISES_TAG,
    SPHINX_RENDER_RETURNS_TAG,
    SPHINX_RENDER_RTYPE_TAG,
    SPHINX_RENDER_TYPE_TAG,
)
from docstring_tailor.ir_model import (
    DocstringNode,
    NamedParagraph,
    SimpleList,
    StructuredList,
    StructuredListError,
    StructuredListParameter,
)
from docstring_tailor.renderer.base_renderer import DocstringRendererBase
from docstring_tailor.utils.utils_formatting import format_text


class SphinxDocstringRenderer(DocstringRendererBase):
    """Renders a parsed docstring IR into the Sphinx/reST docstring format.

    Overrides the two section renderers whose physical shape is Sphinx-specific
    (structured lists become flat field lists; named paragraphs become '..
    directive::' admonitions) and satisfies the three abstract hooks with
    minimal stubs, since the shared header/entry machinery those hooks feed is
    bypassed by the overrides. All flat-content rendering is inherited.
    """

    def _join_rendered_nodes(
        self, nodes: list[DocstringNode], rendered_parts: list[str]
    ) -> str:
        """Joins rendered node strings, keeping consecutive field-list blocks
        contiguous.

        Sphinx splits documented parameters, returns, and raises into separate
        StructuredList nodes, but reST renders them as one uninterrupted field
        list with no blank lines between the groups. So a junction between two
        StructuredList nodes uses the single line separator; every other
        junction defers to the shared base behaviour (blank line, except the
        SimpleList adjacency the base already special-cases).

        Args:
            nodes (list[DocstringNode]): The IR nodes corresponding to
                rendered_parts, in the same order.
            rendered_parts (list[str]): Each node's rendered string form, in
                order.

        Returns:
            joined (str): The fully joined string.
        """

        if not rendered_parts:
            return ""

        joined = rendered_parts[0]

        for previous, node, part in zip(nodes, nodes[1:], rendered_parts[1:]):
            if isinstance(previous, StructuredList) and isinstance(
                node, StructuredList
            ):
                separator = self._line_separator
            elif isinstance(node, SimpleList) and not node.has_leading_blank_line:
                separator = self._line_separator
            else:
                separator = self._paragraph_separator

            joined += separator + part

        return joined

    @property
    def _section_body_indented(self) -> bool:
        """Sphinx field lists and directive bodies are rendered by the overrides
        in this class, not by the shared header-plus-body machinery, so this
        hook is never consulted. Returns False as a neutral default.

        Returns:
            result (bool): Always False for Sphinx.
        """

        result = False

        return result

    def _render_section_header(self, name: str) -> str:
        """Unused for Sphinx: field lists and directives render their own
        markers inline, so there is no standalone section header. Kept to
        satisfy the abstract contract.

        Args:
            name (str): The section keyword or header text.

        Returns:
            header (str): The name unchanged.
        """

        return name

    def _render_structured_list_entry(
        self, entry: StructuredListParameter | StructuredListError
    ) -> str:
        """Unused for Sphinx: _render_structured_list below renders each field
        line directly, since a single IR entry maps to one or two physical field
        lines (':param' and optionally ':type'). Kept to satisfy the abstract
        contract.

        Args:
            entry (StructuredListParameter | StructuredListError): A single
                parsed entry.

        Returns:
            rendered (str): An empty string.
        """

        return ""

    def _render_field(self, tag: str, body: str) -> str:
        """Renders a single reST field line, wrapping its body with a hanging
        indent so continuation lines align under the body rather than the tag.

        Args:
            tag (str): The full field tag including trailing colon and space,
                e.g. ':param x: ' or ':returns: '.
            body (str): The field body text.

        Returns:
            rendered (str): The wrapped, indented field line.
        """

        text = f"{tag}{body}"
        rendered = format_text(
            text=text,
            wrap_width=self._wrap_width,
            line_separator=self._line_separator,
            subsequent_indent=self._indent_unit,
        )

        return rendered

    def _render_parameter_fields(self, entry: StructuredListParameter) -> list[str]:
        """Renders one parameter entry as its ':param' line plus an optional
        ':type' line.

        The ':type' line is emitted only when the entry has both a name and a
        documented type; an undocumented type (None) produces no ':type' line.
        An entry with no name at all cannot form a valid ':type name:' pairing,
        so only the ':param' line is emitted, using the type as the parameter
        token when present -- this arises only when converting from a source
        style whose parameter syntax could not carry a name (e.g. a Google 'y:
        desc' line with no '(type)').

        Args:
            entry (StructuredListParameter): A parameter entry.

        Returns:
            lines (list[str]): One or two rendered field lines.
        """

        param_token = entry.name if entry.name is not None else entry.type or ""
        lines = [
            self._render_field(
                f"{SPHINX_RENDER_PARAM_TAG} {param_token}: ", entry.description
            )
        ]

        if entry.name is not None and entry.type is not None:
            lines.append(
                self._render_field(
                    f"{SPHINX_RENDER_TYPE_TAG} {entry.name}: ", entry.type
                )
            )

        return lines

    def _render_return_fields(self, entry: StructuredListParameter) -> list[str]:
        """Renders the return entry as a ':returns' line plus an optional
        ':rtype' line.

        Args:
            entry (StructuredListParameter): The unnamed return entry.

        Returns:
            lines (list[str]): One or two rendered field lines.
        """

        lines = [self._render_field(f"{SPHINX_RENDER_RETURNS_TAG} ", entry.description)]

        if entry.type is not None:
            lines.append(self._render_field(f"{SPHINX_RENDER_RTYPE_TAG} ", entry.type))

        return lines

    def _render_error_field(self, entry: StructuredListError) -> str:
        """Renders a raised-exception entry as a ':raises Exc:' field line.

        Args:
            entry (StructuredListError): A raised-exception entry.

        Returns:
            rendered (str): The rendered field line.
        """
        if entry.error_type is not None:
            rendered = self._render_field(
                f"{SPHINX_RENDER_RAISES_TAG} {entry.error_type}: ", entry.description
            )
        else:
            rendered = self._render_field(
                f"{SPHINX_RENDER_RAISES_TAG}: ", entry.description
            )

        return rendered

    def _render_structured_list(self, section: StructuredList) -> str:
        """Renders a structured list section as a flat reST field list.

        Dispatches by the section's canonical keyword: Returns entries render as
        ':returns'/':rtype', Raises entries as ':raises', and everything else
        (Parameters/Attributes) as ':param'/':type'. Field lines are joined with
        the current line separator so the whole block sits at one indent level,
        exactly as reST field lists appear.

        Args:
            section (StructuredList): A parsed structured list node.

        Returns:
            rendered (str): The rendered field-list block.
        """

        lines: list[str] = []

        for entry in section.entries:
            if isinstance(entry, StructuredListError):
                lines.append(self._render_error_field(entry))
            elif section.keyword == SPHINX_KEYWORD_RETURNS:
                lines.extend(self._render_return_fields(entry))
            else:
                lines.extend(self._render_parameter_fields(entry))

        rendered = self._line_separator.join(lines)

        return rendered

    def _render_named_paragraph(self, section: NamedParagraph) -> str:
        """Renders a named paragraph as a reST admonition directive.

        Emits the '.. directive::' marker, then the body one indent level
        deeper, reusing the shared _render_node dispatch so prose, code blocks,
        and simple lists inside the admonition render identically to anywhere
        else. A header with no known directive mapping falls back to a generic
        '.. <lowercased header>::' marker so content is never dropped.

        Args:
            section (NamedParagraph): A parsed named paragraph node.

        Returns:
            rendered (str): The rendered admonition block.
        """

        directive = SPHINX_HEADER_DIRECTIVES.get(
            section.header, f".. {section.header.lower()}::"
        )

        with self._nested_body():
            rendered_body_nodes = [self._render_node(node) for node in section.body]
            body = self._join_rendered_nodes(section.body, rendered_body_nodes)

        rendered = directive + "\n" + self._base_indent_level + self._indent_unit + body

        return rendered
