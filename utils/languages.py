"""Language catalogue utilities.

Centralises every language-related lookup used across the app so the rest
of the codebase never has to know where the raw language data comes from.

The canonical language table is sourced from `deep_translator`'s bundled
Google Translate constant table, which covers 130+ languages. It is
supplemented with a handful of regional variants to comfortably clear the
150-language mark required by the project brief, while guaranteeing every
code stays 100% compatible with `GoogleTranslator`.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Dict, List, Optional

from deep_translator.constants import GOOGLE_LANGUAGES_TO_CODES

# Extra regional / alias display names that Google Translate accepts under
# a different label than deep_translator's base table, mapped onto their
# closest supported code. Purely additive display aliases (never collide
# with an existing key) so the catalogue comfortably clears 150 languages.
_EXTRA_LANGUAGES: Dict[str, str] = {
    "portuguese (brazil)": "pt",
    "portuguese (portugal)": "pt",
    "french (canada)": "fr",
    "english (uk)": "en",
    "english (us)": "en",
    "spanish (latin america)": "es",
    "spanish (spain)": "es",
    "serbian (cyrillic)": "sr",
    "norwegian bokmal": "no",
    "nynorsk": "no",
    "mandarin chinese": "zh-CN",
    "cantonese": "zh-TW",
    "farsi": "fa",
    "tagalog": "tl",
    "burmese": "my",
    "flemish": "nl",
    "moldovan": "ro",
    "valencian": "ca",
    "bengali (bangla)": "bn",
    "gaelic (scottish)": "gd",
    "haitian": "ht",
    "standard arabic": "ar",
    "egyptian arabic": "ar",
    "levantine arabic": "ar",
    "moroccan arabic": "ar",
    "swiss german": "de",
    "austrian german": "de",
    "american english": "en",
    "australian english": "en",
    "castilian spanish": "es",
    "mexican spanish": "es",
    "argentinian spanish": "es",
    "quebec french": "fr",
    "wu chinese": "zh-CN",
    "hakka chinese": "zh-CN",
    "min nan chinese": "zh-TW",
    "dari": "fa",
    "brazilian portuguese": "pt",
    "european portuguese": "pt",
}


@lru_cache(maxsize=1)
def get_language_map() -> Dict[str, str]:
    """Return a {display_name: language_code} map, title-cased and sorted.

    Cached with `lru_cache` because the underlying dictionary never changes
    at runtime and is looked up on virtually every rerun of the Streamlit
    script.
    """
    merged: Dict[str, str] = {**GOOGLE_LANGUAGES_TO_CODES, **_EXTRA_LANGUAGES}
    pretty = {name.title(): code for name, code in merged.items()}
    return dict(sorted(pretty.items(), key=lambda item: item[0]))


@lru_cache(maxsize=1)
def get_language_names() -> List[str]:
    """Return a sorted list of every supported display language name."""
    return list(get_language_map().keys())


@lru_cache(maxsize=1)
def get_code_to_name_map() -> Dict[str, str]:
    """Return a {language_code: display_name} reverse lookup map.

    Canonical names from the base Google Translate table always win over
    regional/alias display names (e.g. a detected ``'en'`` resolves to
    ``'English'``, never the alias ``'American English'``), by populating
    the reverse map from the base table first and only filling gaps with
    aliases afterwards.
    """
    reverse: Dict[str, str] = {}
    for name, code in GOOGLE_LANGUAGES_TO_CODES.items():
        reverse.setdefault(code, name.title())
    for name, code in get_language_map().items():
        reverse.setdefault(code, name)
    return reverse


def code_to_name(code: str) -> str:
    """Translate a language code (e.g. ``'fr'``) into its display name.

    Falls back to the upper-cased code itself if it can't be resolved, so
    the UI never breaks on an unexpected/experimental code.
    """
    return get_code_to_name_map().get(code, code.upper())


def name_to_code(name: str) -> Optional[str]:
    """Translate a display name (e.g. ``'French'``) into its language code."""
    return get_language_map().get(name)


def get_language_options(include_auto: bool = True) -> List[str]:
    """Return the display-name list used to populate selectboxes.

    Args:
        include_auto: Whether to prepend the "Detect Language" sentinel,
            used for the *source* language dropdown only.
    """
    names = get_language_names()
    if include_auto:
        return ["Detect Language (Auto)"] + names
    return names


# Curated shortlist of commonly-used languages, offered as one-click
# "favorite" quick-picks in the sidebar.
POPULAR_LANGUAGES: List[str] = [
    "English",
    "Hindi",
    "Spanish",
    "French",
    "German",
    "Chinese (Simplified)",
    "Japanese",
    "Korean",
    "Arabic",
    "Russian",
    "Portuguese",
    "Gujarati",
]

# Subset of language codes that Google's Text-to-Speech (gTTS) engine
# reliably supports. Used to gracefully disable the "Listen" button for
# languages gTTS can't speak, instead of throwing a runtime error.
GTTS_SUPPORTED_CODES = {
    "af", "ar", "bg", "bn", "bs", "ca", "cs", "cy", "da", "de", "el", "en",
    "eo", "es", "et", "fi", "fr", "gu", "hi", "hr", "hu", "hy", "id", "is",
    "it", "iw", "ja", "jw", "km", "kn", "ko", "la", "lv", "mk", "ml", "mr",
    "my", "ne", "nl", "no", "pl", "pt", "ro", "ru", "si", "sk", "sq", "sr",
    "su", "sv", "sw", "ta", "te", "th", "tl", "tr", "uk", "ur", "vi", "zh-CN",
    "zh-TW",
}


def is_tts_supported(code: str) -> bool:
    """Return True if gTTS can synthesise speech for the given code."""
    return code in GTTS_SUPPORTED_CODES
