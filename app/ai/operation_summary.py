"""AI-ready helpers for generating human-readable operation summaries.

This module is intentionally small and opinionated; it provides a simple
way to convert numeric operation results (e.g., lot validation) into a
short, human-friendly summary sentence.
"""

from __future__ import annotations


def _plural(value: int, singular: str, plural: str | None = None) -> str:
    """Return the value with a properly pluralized noun."""
    noun = singular if value == 1 else (plural or f"{singular}s")
    return f"{value} {noun}"


def summarize_lot_validation(*, scanned: int, unknown: int, duplicates: int, missing: int) -> str:
    """Generate a short, human-readable summary of lot validation results.

    Example output:
        "84 animals scanned, 2 unknown, 1 duplicate, 3 missing."

    This is intentionally simple and designed for display in UIs or chatbots.
    """

    parts = [
        f"{_plural(scanned, 'animal')} scanned",
        f"{unknown} unknown",
        f"{duplicates} duplicate",
        f"{missing} missing",
    ]

    return ", ".join(parts) + "."
