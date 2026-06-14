""" """

from dataclasses import dataclass

# Hierarchy level 2

@dataclass
class Argument:
    name: str
    type: str | None
    description: str

# Hierarchy level 1

@dataclass
class SummaryLine:
    text: str

@dataclass
class Paragraph:
    text: str

@dataclass
class Arguments:
    arguments: list[Argument]