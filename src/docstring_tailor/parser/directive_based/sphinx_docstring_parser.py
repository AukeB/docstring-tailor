"""Contains the Sphinx/reST-style docstring parser.

Sphinx docstrings do not mark sections with headings and indentation the way
Google and NumPy do; they use reST field lists (':param name: ...', ':returns:
...', ':raises Exc: ...') and admonition directives ('.. note::', '.. warning::'
...). This parser therefore does not extend IndentationBasedParser -- its
section detection is directive-based rather than indentation-based -- but it
does extend the shared DocstringParserBase, reusing that base's flat-content
pipeline unchanged for every run of ordinary prose, code block, or simple list
that sits between the directives. Only the directive scanning and field-list
grouping below are Sphinx-specific.

Types are optional in reST: a parameter may be typed with a separate ':type
name:' field, with an inline type ':param <type> <name>:', or not at all when
the signature's PEP 484 hints carry the type. All three forms are accepted, and
an undocumented type becomes None in the IR (never fabricated), consistent with
StructuredListParameter.type being str | None.
"""

from inspect import cleandoc

from docstring_tailor.constants import (
    DOCSTRING_DELIMITER_LENGTH,
    SPHINX_DIRECTIVE_HEADERS,
    SPHINX_FIELD_TAGS,
    SPHINX_KEYWORD_PARAMETERS,
    SPHINX_KEYWORD_RAISES,
    SPHINX_KEYWORD_RETURNS,
    SPHINX_PARAM_TAGS,
    SPHINX_RAISE_TAGS,
    SPHINX_RETURN_TAGS,
    SPHINX_RTYPE_TAGS,
    SPHINX_TYPE_TAGS,
)
from docstring_tailor.ir_model import (
    DocstringNode,
    NamedParagraph,
    StructuredList,
    StructuredListError,
    StructuredListParameter,
)
from docstring_tailor.parser.docstring_parser_base import DocstringParserBase


class SphinxDocstringParser(DocstringParserBase):
    """Parses Sphinx/reST-style docstrings into a typed intermediate
    representation.

    Extends DocstringParserBase (not IndentationBasedParser) because Sphinx
    detects sections by directive markers rather than by heading indentation.
    The parse pipeline scans top-level lines into three kinds of segment --
    flat-content runs, a single contiguous field-list block, and admonition
    directive blocks -- then dispatches each: flat content through the inherited
    _parse_flat_content, field-list blocks through style-specific field pairing,
    and directives into NamedParagraph nodes whose bodies reuse the inherited
    _parse_named_paragraph_body.
    """

    def parse(self, content: str) -> list[DocstringNode]:
        """Parses a raw Sphinx docstring string into a typed IR.

        Strips triple-quote delimiters, normalises indentation with cleandoc,
        and delegates to _parse_top_level.

        Args:
            content (str): Raw docstring string including triple-quote
                delimiters.

        Returns:
            ir (list[DocstringNode]): Fully parsed and typed IR.
        """
        docstring_body = cleandoc(
            content[DOCSTRING_DELIMITER_LENGTH:-DOCSTRING_DELIMITER_LENGTH]
        )

        ir = self._parse_top_level(docstring_body)

        return ir

    @staticmethod
    def _line_tag(line: str) -> str | None:
        """Returns the field tag opening a line, if the line is a field line.

        A field line starts (after leading whitespace) with a ':'-delimited tag
        such as ':param' or ':returns'. The tag returned is the leading token up
        to the first space or the closing ':', lowercased for case-insensitive
        matching against the known tag sets.

        Args:
            line (str): A single raw line.

        Returns:
            tag (str | None): The lowercased leading tag (e.g. ':param'), or
                None if the line does not open with a field tag.
        """
        stripped = line.strip()

        if not stripped.startswith(":"):
            return None

        # The tag is the text up to the first space; for ':param x:' that is
        # ':param', for ':rtype:' that is ':rtype:'. Trim any trailing colon so
        # both ':rtype:' and ':param' normalise to a bare ':tag'.
        head = stripped.split(" ", 1)[0]
        tag = head.rstrip(":").lower()
        tag = tag if tag.startswith(":") else f":{tag}"

        return tag

    @staticmethod
    def _line_directive(line: str) -> str | None:
        """Returns the admonition directive opening a line, if any.

        Args:
            line (str): A single raw line.

        Returns:
            directive (str | None): The directive marker (e.g. '.. note::'),
                normalised to its canonical lowercase form, or None if the line
                is not a recognised admonition directive.
        """
        stripped = line.strip()

        for directive in SPHINX_DIRECTIVE_HEADERS:
            if stripped.lower().startswith(directive):
                return directive

        return None

    def _is_field_line(self, line: str) -> bool:
        """Whether a line opens a reST field-list entry.

        Args:
            line (str): A single raw line.

        Returns:
            result (bool): True if the line begins a known field tag.
        """
        tag = self._line_tag(line)
        result = tag is not None and tag in SPHINX_FIELD_TAGS

        return result

    def _split_field_body(self, line: str) -> tuple[str, str]:
        """Splits a field line into its tag-with-argument head and its body.

        A reST field line has the shape ':tag arg: body'. This splits on the
        second colon (the one closing the field name), returning the raw head
        (everything up to and including that colon, minus the colons themselves
        as appropriate) and the trailing body text.

        Args:
            line (str): A single raw field line, e.g. ':param int x: the value'.

        Returns:
            parts (tuple[str, str]): (head, body) where head is the text between
                the opening and closing colons (e.g. 'param int x') and body is
                the description after the closing colon.
        """
        stripped = line.strip()
        # Drop the opening colon, then split on the next colon which closes the
        # field name. Everything before is the head, everything after the body.
        without_open = stripped[1:]
        head, _, body = without_open.partition(":")

        return head.strip(), body.strip()

    def _collect_field_block(
        self, lines: list[str], start: int
    ) -> tuple[list[tuple[str, str]], int]:
        """Collects a contiguous field-list block starting at the given index.

        Gathers each field line together with any indented continuation lines
        that follow it, joining continuations into the field's body with single
        spaces. Blank lines are tolerated within the block as long as a further
        field line follows; the block ends at the first line that is neither a
        field line, a continuation, nor a blank line before another field.

        Args:
            lines (list[str]): All top-level lines.
            start (int): Index of the first field line of the block.

        Returns:
            block (tuple[list[tuple[str, str]], int]): A list of (head, body)
                pairs for each field in the block, and the index of the first
                line after the block.
        """
        fields: list[tuple[str, str]] = []
        index = start
        head: str | None = None
        body_parts: list[str] = []

        while index < len(lines):
            line = lines[index]

            if not line.strip():
                if self._blank_continues_block(lines, index):
                    index += 1
                    continue
                break

            if self._is_field_line(line):
                self._append_field(fields, head, body_parts)
                head, body = self._split_field_body(line)
                body_parts = [body] if body else []
            elif head is not None and line[:1].isspace():
                body_parts.append(line.strip())
            else:
                break

            index += 1

        self._append_field(fields, head, body_parts)

        return fields, index

    def _blank_continues_block(self, lines: list[str], index: int) -> bool:
        """Whether a blank line at index is followed by another field line.

        Args:
            lines (list[str]): All top-level lines.
            index (int): Index of the blank line.

        Returns:
            result (bool): True if the next non-blank line is a field line.
        """
        lookahead = index + 1
        while lookahead < len(lines) and not lines[lookahead].strip():
            lookahead += 1

        result = lookahead < len(lines) and self._is_field_line(lines[lookahead])

        return result

    @staticmethod
    def _append_field(
        fields: list[tuple[str, str]], head: str | None, body_parts: list[str]
    ) -> None:
        """Appends a completed (head, body) field to the accumulator, if any.

        Args:
            fields (list[tuple[str, str]]): The accumulator to append to.
            head (str | None): The current field head, or None if none is open.
            body_parts (list[str]): The current field's body fragments.
        """
        if head is not None:
            fields.append((head, " ".join(body_parts).strip()))

    def _tag_of_head(self, head: str) -> str:
        """Returns the normalised field tag from a collected head string.

        Args:
            head (str): The head portion of a field, e.g. 'param int x' or
                'rtype'.

        Returns:
            tag (str): The leading tag with a colon prefix, lowercased, e.g.
                ':param'.
        """
        first_token = head.split(" ", 1)[0].lower()
        tag = f":{first_token}"

        return tag

    def _parse_param_head(self, head: str) -> tuple[str, str | None]:
        """Extracts the parameter name and optional inline type from a :param
        head.

        Supports both ':param name' (name only) and ':param <type> <name>'
        (inline type). When two or more tokens follow the tag, all but the last
        are treated as the type and the final token as the name; a single token
        is the name with no type.

        Args:
            head (str): The head of a :param field, e.g. 'param x' or 'param int
                x'.

        Returns:
            parsed (tuple[str, str | None]): (name, inline_type) where
                inline_type is None when no inline type was given.
        """
        tokens = head.split()
        # tokens[0] is the tag itself ('param'); the rest describe the entry.
        rest = tokens[1:]

        if len(rest) == 1:
            return rest[0], None

        name = rest[-1]
        inline_type = " ".join(rest[:-1])

        return name, inline_type

    def _apply_param_field(
        self,
        head: str,
        body: str,
        parameters: list[StructuredListParameter],
        param_index_by_name: dict[str, int],
    ) -> None:
        """Adds a ':param' field as a new parameter entry.

        Args:
            head (str): The field head, e.g. 'param int x'.
            body (str): The field description.
            parameters (list[StructuredListParameter]): The accumulator to
                append to.
            param_index_by_name (dict[str, int]): Maps parameter name to its
                index in parameters, so a later ':type' field can find it.
        """
        name, inline_type = self._parse_param_head(head)
        param_index_by_name[name] = len(parameters)
        parameters.append(
            StructuredListParameter(name=name, type=inline_type, description=body)
        )

    @staticmethod
    def _apply_type_field(
        head: str,
        body: str,
        parameters: list[StructuredListParameter],
        param_index_by_name: dict[str, int],
    ) -> None:
        """Attaches a ':type name:' field's type to its matching parameter.

        Args:
            head (str): The field head, e.g. 'type x'.
            body (str): The type text.
            parameters (list[StructuredListParameter]): The parameter
                accumulator, mutated in place.
            param_index_by_name (dict[str, int]): Maps parameter name to index.
        """
        type_name = head.split(" ", 1)[1].strip() if " " in head else ""
        target = param_index_by_name.get(type_name)

        if target is not None:
            existing = parameters[target]
            parameters[target] = StructuredListParameter(
                name=existing.name, type=body, description=existing.description
            )

    def _parse_field_block(self, fields: list[tuple[str, str]]) -> list[DocstringNode]:
        """Groups a collected field block into StructuredList nodes.

        Pairs ':param name' with its matching ':type name', and ':returns' with
        ':rtype', collapsing each pair into one StructuredListParameter. Every
        ':raises Exc' becomes a StructuredListError. Emits up to three
        StructuredList nodes -- Parameters, Returns, Raises -- in that order,
        omitting any that have no entries. An undocumented type stays None.

        Args:
            fields (list[tuple[str, str]]): (head, body) pairs for each field in
                the block.

        Returns:
            nodes (list[DocstringNode]): The StructuredList nodes for this
                block.
        """
        parameters: list[StructuredListParameter] = []
        param_index_by_name: dict[str, int] = {}
        return_entry: StructuredListParameter | None = None
        errors: list[StructuredListError] = []

        for head, body in fields:
            tag = self._tag_of_head(head)

            if tag in SPHINX_PARAM_TAGS:
                self._apply_param_field(head, body, parameters, param_index_by_name)
            elif tag in SPHINX_TYPE_TAGS:
                self._apply_type_field(head, body, parameters, param_index_by_name)
            elif tag in SPHINX_RETURN_TAGS or tag in SPHINX_RTYPE_TAGS:
                return_entry = self._apply_return_field(tag, body, return_entry)
            elif tag in SPHINX_RAISE_TAGS:
                errors.append(self._make_error(head, body))

        return self._assemble_field_nodes(parameters, return_entry, errors)

    @staticmethod
    def _apply_return_field(
        tag: str, body: str, return_entry: StructuredListParameter | None
    ) -> StructuredListParameter:
        """Applies a ':returns' or ':rtype' field to the running return entry.

        ':returns' sets the description while preserving any type already seen;
        ':rtype' sets the type while preserving any description already seen.
        The two fields may appear in either order.

        Args:
            tag (str): The normalised field tag.
            body (str): The field body.
            return_entry (StructuredListParameter | None): The return entry so
                far, or None if neither field has been seen yet.

        Returns:
            entry (StructuredListParameter): The updated return entry.
        """
        existing_type = return_entry.type if return_entry is not None else None
        existing_desc = return_entry.description if return_entry is not None else ""

        if tag in SPHINX_RTYPE_TAGS:
            return StructuredListParameter(
                name=None, type=body, description=existing_desc
            )

        return StructuredListParameter(name=None, type=existing_type, description=body)

    @staticmethod
    def _make_error(head: str, body: str) -> StructuredListError:
        """Builds a StructuredListError from a ':raises Exc' field.

        Args:
            head (str): The field head, e.g. 'raises ValueError'.
            body (str): The field description.

        Returns:
            error (StructuredListError): The parsed error entry.
        """
        error_type = head.split(" ", 1)[1].strip() if " " in head else ""
        error = StructuredListError(error_type=error_type, description=body)

        return error

    @staticmethod
    def _assemble_field_nodes(
        parameters: list[StructuredListParameter],
        return_entry: StructuredListParameter | None,
        errors: list[StructuredListError],
    ) -> list[DocstringNode]:
        """Assembles the grouped field entries into StructuredList nodes.

        Emits Parameters, Returns, and Raises nodes in that fixed order,
        skipping any group with no entries.

        Args:
            parameters (list[StructuredListParameter]): Collected parameters.
            return_entry (StructuredListParameter | None): The single return
                entry, if any.
            errors (list[StructuredListError]): Collected raises entries.

        Returns:
            nodes (list[DocstringNode]): The StructuredList nodes.
        """
        nodes: list[DocstringNode] = []

        if parameters:
            nodes.append(
                StructuredList(keyword=SPHINX_KEYWORD_PARAMETERS, entries=parameters)
            )

        if return_entry is not None:
            nodes.append(
                StructuredList(keyword=SPHINX_KEYWORD_RETURNS, entries=[return_entry])
            )

        if errors:
            nodes.append(StructuredList(keyword=SPHINX_KEYWORD_RAISES, entries=errors))

        return nodes

    def _collect_directive_block(self, lines: list[str], start: int) -> tuple[str, int]:
        """Collects an admonition directive block and its indented body.

        The directive line itself may carry trailing content after the marker
        (e.g. '.. note:: inline text'); that and every subsequent indented line
        form the body. The block ends at the first non-indented, non-blank line.

        Args:
            lines (list[str]): All top-level lines.
            start (int): Index of the directive line.

        Returns:
            block (tuple[str, int]): The raw body content (directive marker
                stripped, original indentation of body lines preserved), and the
                index of the first line after the block.
        """
        directive = self._line_directive(lines[start])
        assert directive is not None
        first_line = lines[start].strip()
        inline = first_line[len(directive) :].strip()

        body_lines: list[str] = []
        if inline:
            body_lines.append(inline)

        index = start + 1
        while index < len(lines):
            line = lines[index]
            if not line.strip():
                body_lines.append("")
                index += 1
                continue
            if len(line) - len(line.lstrip()) > 0:
                body_lines.append(line)
                index += 1
            else:
                break

        # Trim trailing blanks.
        while body_lines and not body_lines[-1].strip():
            body_lines.pop()

        body_content = "\n".join(body_lines)

        return body_content, index

    def _parse_directive_block(self, lines: list[str], start: int) -> NamedParagraph:
        """Parses an admonition directive into a NamedParagraph node.

        Maps the directive to its canonical header and parses the body through
        the inherited _parse_named_paragraph_body, so prose, code blocks, and
        lists inside the admonition classify exactly as they do anywhere else.

        Args:
            lines (list[str]): All top-level lines.
            start (int): Index of the directive line.

        Returns:
            named_paragraph (NamedParagraph): The parsed admonition node.
        """
        directive = self._line_directive(lines[start])
        assert directive is not None
        header = SPHINX_DIRECTIVE_HEADERS[directive]

        body_content, _ = self._collect_directive_block(lines, start)
        body = self._parse_named_paragraph_body(body_content)

        named_paragraph = NamedParagraph(header=header, body=body)

        return named_paragraph

    def _parse_top_level(self, content: str) -> list[DocstringNode]:
        """Parses top-level Sphinx docstring content by directive scanning.

        Walks the lines once, accumulating runs of ordinary content and
        dispatching field-list blocks and admonition directives to their style-
        specific parsers as they are encountered. Ordinary content runs are
        flushed through the inherited flat-content pipeline, preserving prose,
        code blocks, and simple lists exactly as in the other styles.

        Args:
            content (str): Raw docstring body with triple-quote delimiters
                stripped.

        Returns:
            nodes (list[DocstringNode]): Fully parsed IR.
        """
        lines = content.splitlines()
        nodes: list[DocstringNode] = []
        flat_buffer: list[str] = []
        index = 0

        def flush_flat() -> None:
            if any(line.strip() for line in flat_buffer):
                nodes.extend(self._parse_flat_content("\n".join(flat_buffer)))
            flat_buffer.clear()

        while index < len(lines):
            line = lines[index]

            if self._is_field_line(line):
                flush_flat()
                fields, index = self._collect_field_block(lines, index)
                nodes.extend(self._parse_field_block(fields))
                continue

            if self._line_directive(line) is not None:
                flush_flat()
                nodes.append(self._parse_directive_block(lines, index))
                _, index = self._collect_directive_block(lines, index)
                continue

            flat_buffer.append(line)
            index += 1

        flush_flat()

        return nodes
