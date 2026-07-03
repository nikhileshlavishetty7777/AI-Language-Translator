"""Translation service layer.

Wraps `deep_translator.GoogleTranslator` and `langdetect` behind a small,
typed, exception-safe API so the UI layer never has to deal with raw
third-party exceptions or edge cases (empty strings, oversized inputs,
network hiccups, unsupported languages, etc).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from deep_translator import GoogleTranslator
from deep_translator.exceptions import (
    LanguageNotSupportedException,
    NotValidPayload,
    RequestError,
    TranslationNotFound,
)
from langdetect import DetectorFactory, LangDetectException, detect_langs

from utils.languages import code_to_name

# Make langdetect deterministic across runs (otherwise short strings can
# occasionally flip between similar languages on repeated calls).
DetectorFactory.seed = 0

MAX_INPUT_CHARACTERS = 5000


class TranslationError(Exception):
    """Raised for any recoverable translation failure.

    Carries a human-friendly message intended to be shown directly in the
    Streamlit UI via `st.error`.
    """


@dataclass(frozen=True)
class DetectionResult:
    """Result of automatic source-language detection."""

    code: str
    name: str
    confidence: float


@dataclass(frozen=True)
class TranslationResult:
    """Result of a successful translation request."""

    original_text: str
    translated_text: str
    source_code: str
    source_name: str
    target_code: str
    target_name: str
    detected: bool


def detect_language(text: str) -> DetectionResult:
    """Detect the language of `text` using a local statistical model.

    Uses `langdetect` (no network / API key required) rather than an extra
    remote call, keeping detection fast and independent of translation
    provider rate limits.

    Raises:
        TranslationError: if the text is empty or the language cannot be
            confidently determined (e.g. numbers-only input).
    """
    cleaned = (text or "").strip()
    if not cleaned:
        raise TranslationError("Please enter some text before detecting its language.")

    try:
        candidates = detect_langs(cleaned)
        best = candidates[0]
        code = _normalize_detect_code(best.lang)
        return DetectionResult(code=code, name=code_to_name(code), confidence=round(best.prob, 2))
    except LangDetectException as exc:
        raise TranslationError(
            "Could not confidently detect the language of this text. "
            "Try entering a longer or clearer sentence."
        ) from exc


def _normalize_detect_code(lang_code: str) -> str:
    """Map a few langdetect codes to their Google Translate equivalents."""
    overrides = {"zh-cn": "zh-CN", "zh-tw": "zh-TW", "he": "iw"}
    return overrides.get(lang_code, lang_code)


def validate_translation_input(text: str) -> None:
    """Validate raw user input before sending it to the translator.

    Raises:
        TranslationError: describing exactly why the input is invalid.
    """
    if text is None or not text.strip():
        raise TranslationError("Please enter some text to translate.")
    if len(text) > MAX_INPUT_CHARACTERS:
        raise TranslationError(
            f"Input is too long ({len(text)} characters). "
            f"Please limit text to {MAX_INPUT_CHARACTERS} characters."
        )


def translate_text(
    text: str,
    source_code: str,
    target_code: str,
) -> TranslationResult:
    """Translate `text` from `source_code` to `target_code`.

    Args:
        text: Raw text entered by the user.
        source_code: A language code, or the literal string ``"auto"`` to
            trigger automatic source-language detection.
        target_code: The destination language code.

    Returns:
        A populated `TranslationResult`.

    Raises:
        TranslationError: for any invalid input or provider-side failure,
            already formatted for direct display in the UI.
    """
    validate_translation_input(text)

    if source_code == target_code and source_code != "auto":
        raise TranslationError("Source and target languages must be different.")

    detected = source_code == "auto"
    resolved_source_code = source_code

    try:
        if detected:
            detection = detect_language(text)
            resolved_source_code = detection.code

        translator = GoogleTranslator(source=source_code, target=target_code)
        translated = translator.translate(text)

        if not translated:
            raise TranslationError("The translation service returned an empty result. Please try again.")

        return TranslationResult(
            original_text=text,
            translated_text=translated,
            source_code=resolved_source_code,
            source_name=code_to_name(resolved_source_code),
            target_code=target_code,
            target_name=code_to_name(target_code),
            detected=detected,
        )

    except TranslationError:
        raise
    except LanguageNotSupportedException as exc:
        raise TranslationError("One of the selected languages is not supported by the translation engine.") from exc
    except NotValidPayload as exc:
        raise TranslationError("The text entered isn't valid for translation. Please check it and try again.") from exc
    except TranslationNotFound as exc:
        raise TranslationError("No translation could be found for this text.") from exc
    except RequestError as exc:
        raise TranslationError("Couldn't reach the translation service. Please check your internet connection and try again.") from exc
    except Exception as exc:  # noqa: BLE001 - final safety net for the UI
        raise TranslationError(f"An unexpected error occurred: {exc}") from exc
