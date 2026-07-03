"""Translation history persistence layer.

History is persisted as JSON on disk (`history/translation_history.json`)
so it survives across Streamlit reruns and app restarts, while also being
mirrored into `st.session_state` for instant, no-IO reads during a session.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd

HISTORY_DIR = Path(__file__).resolve().parent.parent / "history"
HISTORY_FILE = HISTORY_DIR / "translation_history.json"
MAX_HISTORY_ENTRIES = 200


@dataclass
class HistoryEntry:
    """A single saved translation record."""

    timestamp: str
    source_language: str
    target_language: str
    original_text: str
    translated_text: str

    @staticmethod
    def new(source_language: str, target_language: str, original_text: str, translated_text: str) -> "HistoryEntry":
        return HistoryEntry(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            source_language=source_language,
            target_language=target_language,
            original_text=original_text,
            translated_text=translated_text,
        )


class HistoryManager:
    """Reads and writes the translation history JSON store."""

    def __init__(self, history_file: Path = HISTORY_FILE) -> None:
        self.history_file = history_file
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> List[dict]:
        """Load all history entries from disk, newest first.

        Returns an empty list (never raises) if the file is missing or
        corrupted, so a bad/partial write can never crash the app.
        """
        if not self.history_file.exists():
            return []
        try:
            raw = json.loads(self.history_file.read_text(encoding="utf-8"))
            return raw if isinstance(raw, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def save(self, entries: List[dict]) -> None:
        """Persist the given list of entries to disk, capped to the limit."""
        trimmed = entries[:MAX_HISTORY_ENTRIES]
        try:
            self.history_file.write_text(json.dumps(trimmed, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            # Non-fatal: history simply won't persist across restarts this time.
            pass

    def add(self, entry: HistoryEntry) -> List[dict]:
        """Prepend a new entry, persist it, and return the updated list."""
        entries = self.load()
        entries.insert(0, asdict(entry))
        self.save(entries)
        return entries

    def clear(self) -> None:
        """Delete all saved history."""
        self.save([])

    @staticmethod
    def to_dataframe(entries: List[dict]) -> pd.DataFrame:
        """Convert history entries into a display-ready pandas DataFrame."""
        if not entries:
            return pd.DataFrame(
                columns=["Timestamp", "Source", "Target", "Original Text", "Translated Text"]
            )
        df = pd.DataFrame(entries)
        df = df.rename(
            columns={
                "timestamp": "Timestamp",
                "source_language": "Source",
                "target_language": "Target",
                "original_text": "Original Text",
                "translated_text": "Translated Text",
            }
        )
        return df[["Timestamp", "Source", "Target", "Original Text", "Translated Text"]]

    @staticmethod
    def to_csv_bytes(entries: List[dict]) -> bytes:
        """Serialise history entries to CSV bytes for download."""
        df = HistoryManager.to_dataframe(entries)
        return df.to_csv(index=False).encode("utf-8")
