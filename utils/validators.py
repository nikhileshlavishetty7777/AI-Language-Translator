"""Small, reusable input-validation and text-metric helpers."""

from __future__ import annotations


def count_characters(text: str) -> int:
    """Return the character count of `text` (0 for None/empty)."""
    return len(text) if text else 0


def count_words(text: str) -> int:
    """Return the word count of `text` (0 for None/empty/whitespace-only)."""
    if not text:
        return 0
    return len(text.split())


def is_blank(text: str) -> bool:
    """Return True if `text` is None, empty, or whitespace-only."""
    return not text or not text.strip()


def truncate_preview(text: str, max_length: int = 60) -> str:
    """Return a shortened, ellipsis-terminated preview of `text`."""
    if not text:
        return ""
    text = text.strip().replace("\n", " ")
    return text if len(text) <= max_length else f"{text[:max_length].rstrip()}..."
