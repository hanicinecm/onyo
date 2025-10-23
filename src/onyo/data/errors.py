"""Shared error types and validation reporting utilities for the data layer."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, Sequence


class ValidationLevel(str, Enum):
    """Severity levels for validation outcomes."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """Single validation message associated with a specific source file."""

    level: ValidationLevel
    file_path: str
    field: str
    message: str


class ValidationReport:
    """Aggregated validation issues emitted during corpus processing."""

    __slots__ = ("_issues",)

    def __init__(self, issues: Iterable[ValidationIssue] | None = None) -> None:
        """Initialise the report with an optional sequence of issues."""
        self._issues: list[ValidationIssue] = list(issues or [])

    def __iter__(self) -> Iterator[ValidationIssue]:
        """Iterate over collected validation issues."""
        return iter(self._issues)

    def __len__(self) -> int:
        """Return the number of collected validation issues."""
        return len(self._issues)

    def add(self, issue: ValidationIssue) -> None:
        """Append a validation issue to the report."""
        self._issues.append(issue)

    @property
    def issues(self) -> Sequence[ValidationIssue]:
        """Return an immutable view of collected issues."""
        return tuple(self._issues)
