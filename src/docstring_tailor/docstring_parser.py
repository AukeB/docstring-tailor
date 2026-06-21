"""Contains logic for parsing docstrings into a structured IR."""

from docstring_tailor.constants import (
    DOCSTRING_DELIMITER_LENGTH,
    GOOGLE_ITEM_SECTIONS,
    GOOGLE_PLAIN_SECTIONS,
    PYTHON_REPL_PREFIX_START,
    RE_PATTERN_BLANK_LINES,
    RE_PATTERN_FENCE,
)
from docstring_tailor.ir_model import DocstringSection, SectionType
from docstring_tailor.utils.utils_list_detection import is_list


class DocstringParser:
    """Parses a raw docstring string into a typed intermediate representation.

    The parsing pipeline proceeds in stages:
    1. Wrap the raw content in a single UNIDENTIFIED section.
    2. Extract code blocks protected by fence delimiters.
    3. Split remaining UNIDENTIFIED sections on blank lines.
    4. Classify each chunk into its final section type.
    """

    def __init__(
        self,
    ) -> None:
        """Initialises the DocstringParser."""
        pass

    def _relabel_unidentified_as_paragraph(
        self,
        sections: list[DocstringSection],
    ) -> list[DocstringSection]:
        """Relabels any remaining UNIDENTIFIED sections as PARAGRAPH.

        Acts as the final step in the classification pipeline, converting
        anything not yet identified by a prior pass into plain paragraph text.

        Args:
            sections (list[DocstringSection]): Current IR.

        Returns:
            result (list[DocstringSection]): IR with no remaining UNIDENTIFIED sections.
        """
        result = [
            DocstringSection(
                section_type=SectionType.PARAGRAPH, content=section.content
            )
            if section.section_type is SectionType.UNIDENTIFIED
            else section
            for section in sections
        ]

        return result

    def _detect_simple_list_sections(
        self,
        sections: list[DocstringSection],
    ) -> list[DocstringSection]:
        """Identifies UNIDENTIFIED sections containing a bullet or numbered list.

        A section is classified as SIMPLE_LIST if the is_list utility detects
        at least two list markers at the base indentation level.

        Args:
            sections (list[DocstringSection]): Current IR.

        Returns:
            result (list[DocstringSection]): IR with SIMPLE_LIST sections tagged.
        """
        result: list[DocstringSection] = []

        for section in sections:
            if section.section_type is not SectionType.UNIDENTIFIED:
                result.append(section)
                continue

            if is_list(section.content):
                result.append(
                    DocstringSection(
                        section_type=SectionType.SIMPLE_LIST,
                        content=section.content,
                    )
                )
            else:
                result.append(section)

        return result

    def _detect_code_repl_sections(
        self,
        sections: list[DocstringSection],
    ) -> list[DocstringSection]:
        """Identifies UNIDENTIFIED sections containing Python REPL content.

        A section is classified as CODE_REPL if its first line starts with
        the >>> prompt.

        Args:
            sections (list[DocstringSection]): Current IR.

        Returns:
            result (list[DocstringSection]): IR with CODE_REPL sections tagged.
        """
        result: list[DocstringSection] = []

        for section in sections:
            if section.section_type is not SectionType.UNIDENTIFIED:
                result.append(section)
                continue

            first_line = section.content.splitlines()[0].strip()

            if first_line.startswith(PYTHON_REPL_PREFIX_START):
                result.append(
                    DocstringSection(
                        section_type=SectionType.CODE_REPL,
                        content=section.content,
                    )
                )
            else:
                result.append(section)

        return result

    def _detect_structured_list_sections(
        self,
        sections: list[DocstringSection],
    ) -> list[DocstringSection]:
        """Identifies UNIDENTIFIED sections whose first line matches a structured list keyword.

        Structured list sections are headed by a Google-style keyword such as
        Args, Returns, or Raises, followed by indented entries with name, type,
        and description components.

        Args:
            sections (list[DocstringSection]): Current IR.

        Returns:
            result (list[DocstringSection]): IR with STRUCTURED_LIST sections tagged.
        """
        result: list[DocstringSection] = []

        for section in sections:
            if section.section_type is not SectionType.UNIDENTIFIED:
                result.append(section)
                continue

            first_line = section.content.splitlines()[0].strip()

            if first_line.rstrip(":") in GOOGLE_ITEM_SECTIONS:
                result.append(
                    DocstringSection(
                        section_type=SectionType.STRUCTURED_LIST,
                        content=section.content,
                    )
                )
            else:
                result.append(section)

        return result

    def _detect_named_paragraph_sections(
        self,
        sections: list[DocstringSection],
    ) -> list[DocstringSection]:
        """Identifies UNIDENTIFIED sections whose first line matches a named paragraph keyword.

        Named paragraphs are headed by keywords such as Note, Notes, References,
        See Also, Warning, or Warnings, followed by indented plain text content.

        Args:
            sections (list[DocstringSection]): Current IR.

        Returns:
            result (list[DocstringSection]): IR with NAMED_PARAGRAPH sections tagged.
        """
        result: list[DocstringSection] = []

        for section in sections:
            if section.section_type is not SectionType.UNIDENTIFIED:
                result.append(section)
                continue

            first_line = section.content.splitlines()[0].strip()

            if first_line.rstrip(":") in GOOGLE_PLAIN_SECTIONS:
                result.append(
                    DocstringSection(
                        section_type=SectionType.NAMED_PARAGRAPH,
                        content=section.content,
                    )
                )
            else:
                result.append(section)

        return result

    def _categorize_remaining_sections(
        self,
        sections: list[DocstringSection],
    ) -> list[DocstringSection]:
        """Runs all classifiers in order over the current IR.

        Args:
            sections (list[DocstringSection]): Current IR.

        Returns:
            sections (list[DocstringSection]): Fully categorized IR.
        """
        sections = self._detect_named_paragraph_sections(sections)
        sections = self._detect_structured_list_sections(sections)
        sections = self._detect_code_repl_sections(sections)
        sections = self._detect_simple_list_sections(sections)
        sections = self._relabel_unidentified_as_paragraph(sections)

        return sections

    def _split_on_blank_lines(
        self,
        sections: list[DocstringSection],
    ) -> list[DocstringSection]:
        """Splits each UNIDENTIFIED section on blank lines.

        Args:
            sections (list[DocstringSection]): Current IR.

        Returns:
            result (list[DocstringSection]): New IR with UNIDENTIFIED sections
                split into smaller UNIDENTIFIED chunks.
        """
        result: list[DocstringSection] = []

        for section in sections:
            if section.section_type is not SectionType.UNIDENTIFIED:
                result.append(section)
                continue

            chunks = RE_PATTERN_BLANK_LINES.split(section.content)

            for chunk in chunks:
                if chunk.strip():
                    result.append(
                        DocstringSection(
                            section_type=SectionType.UNIDENTIFIED,
                            content=chunk.strip(),
                        )
                    )

        return result

    def _detect_code_block_sections(
        self,
        sections: list[DocstringSection],
    ) -> list[DocstringSection]:
        """Splits UNIDENTIFIED sections on code fences, tagging fenced blocks as CODE_BLOCK.

        Each UNIDENTIFIED section is split using a capturing re.split() on fence
        delimiters, retaining the delimiters as elements. Chunks are iterated with
        a boolean fence tracker to assign the correct section type.

        Args:
            sections (list[DocstringSection]): Current IR.

        Returns:
            result (list[DocstringSection]): New IR with CODE_BLOCK sections extracted.
        """
        result: list[DocstringSection] = []

        for section in sections:
            if section.section_type is not SectionType.UNIDENTIFIED:
                result.append(section)
                continue

            chunks = RE_PATTERN_FENCE.split(section.content)
            in_fence = False

            for chunk in chunks:
                if RE_PATTERN_FENCE.fullmatch(chunk):
                    in_fence = not in_fence
                    continue

                if chunk.strip():
                    section_type = (
                        SectionType.CODE_BLOCK if in_fence else SectionType.UNIDENTIFIED
                    )
                    result.append(
                        DocstringSection(
                            section_type=section_type,
                            content=chunk.strip(),
                        )
                    )

        return result

    def _build_initial_ir(self, content: str) -> list[DocstringSection]:
        """Wraps the raw docstring body in a single UNIDENTIFIED section.

        Args:
            content (str): Raw docstring string including triple-quote delimiters.

        Returns:
            ir (list[DocstringSection]): Single-element IR ready for identification passes.
        """
        content_without_triple_quotes = content[
            DOCSTRING_DELIMITER_LENGTH:-DOCSTRING_DELIMITER_LENGTH
        ].strip()

        ir = [
            DocstringSection(
                section_type=SectionType.UNIDENTIFIED,
                content=content_without_triple_quotes,
            )
        ]

        return ir

    def parse(self, content: str) -> list[DocstringSection]:
        """Parses a raw docstring into a typed IR.

        1. Wraps content in an initial UNIDENTIFIED section.
        2. Extracts fenced code blocks.
        3. Splits remaining content on blank lines.
        4. Classifies all remaining UNIDENTIFIED sections.

        Args:
            content (str): Raw docstring string including triple-quote delimiters.

        Returns:
            ir (list[DocstringSection]): Fully parsed and typed IR.
        """
        ir = self._build_initial_ir(content)
        ir = self._detect_code_block_sections(ir)
        ir = self._split_on_blank_lines(ir)
        ir = self._categorize_remaining_sections(ir)

        return ir
