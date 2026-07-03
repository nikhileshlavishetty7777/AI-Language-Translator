"""Text-to-speech utilities powered by gTTS.

Synthesised audio is produced entirely in-memory (no temp files touching
disk) and handed back as raw MP3 bytes, ready to be streamed straight into
`st.audio` or offered as a download.
"""

from __future__ import annotations

from io import BytesIO

from gtts import gTTS
from gtts.tts import gTTSError

from utils.languages import is_tts_supported


class SpeechSynthesisError(Exception):
    """Raised when audio synthesis fails or the language is unsupported."""


def synthesize_speech(text: str, language_code: str) -> bytes:
    """Convert `text` into spoken MP3 audio bytes for `language_code`.

    Args:
        text: The text to vocalise. Automatically truncated to a sane
            length to keep synthesis fast and API-friendly.
        language_code: A Google Translate language code (e.g. ``'fr'``).

    Returns:
        Raw MP3 audio bytes.

    Raises:
        SpeechSynthesisError: if the language isn't supported by gTTS or
            synthesis otherwise fails (e.g. no network connectivity).
    """
    cleaned = (text or "").strip()
    if not cleaned:
        raise SpeechSynthesisError("There is no text to convert to speech.")

    if not is_tts_supported(language_code):
        raise SpeechSynthesisError(
            "Text-to-speech isn't available for this language yet."
        )

    # gTTS can be slow / noisy on very long passages; cap it generously.
    truncated = cleaned[:3000]

    try:
        # gTTS uses "zh-CN"/"zh-TW" style codes fine, but expects lowercase
        # for most others - GoogleTranslator codes already match gTTS codes
        # for every entry inside GTTS_SUPPORTED_CODES.
        tts = gTTS(text=truncated, lang=language_code)
        buffer = BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer.read()
    except gTTSError as exc:
        raise SpeechSynthesisError(
            "Couldn't generate audio right now. Please check your internet connection and try again."
        ) from exc
    except Exception as exc:  # noqa: BLE001 - final safety net for the UI
        raise SpeechSynthesisError(f"Speech synthesis failed: {exc}") from exc
