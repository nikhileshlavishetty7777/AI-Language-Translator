"""Main translator interface component.

Renders the language selectors, input/output panels, and every action
button (translate, swap, clear, copy, speak, download) for the core
translation workflow.
"""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from components.copy_button import render_copy_button
from utils.history import HistoryEntry, HistoryManager
from utils.languages import get_language_options, is_tts_supported, name_to_code
from utils.translator import TranslationError, translate_text
from utils.tts import SpeechSynthesisError, synthesize_speech
from utils.validators import count_characters, count_words

_history_manager = HistoryManager()


def _swap_languages() -> None:
    """Callback: swap the source and target language selections."""
    source = st.session_state.get("source_lang_name")
    target = st.session_state.get("target_lang_name")

    if source == "Detect Language (Auto)":
        st.toast("Can't swap while source is set to Auto-Detect.", icon="⚠️")
        return

    st.session_state["source_lang_name"] = target
    st.session_state["target_lang_name"] = source
    st.session_state["input_text"] = st.session_state.get("output_text", "")


def _clear_all() -> None:
    """Callback: reset the input/output panels."""
    st.session_state["input_text"] = ""
    st.session_state["output_text"] = ""
    st.session_state["translation_meta"] = None
    st.session_state["audio_bytes"] = None


def render_translator_ui() -> None:
    """Render the full translate tab: selectors, panels, and actions."""
    source_options = get_language_options(include_auto=True)
    target_options = get_language_options(include_auto=False)

    # ---- Language selector row --------------------------------------------
    col_source, col_swap, col_target = st.columns([5, 1, 5])
    with col_source:
        st.selectbox("Translate from", options=source_options, key="source_lang_name")
    with col_swap:
        st.markdown("<div style='height:1.85rem'></div>", unsafe_allow_html=True)
        st.button("🔄", help="Swap languages", on_click=_swap_languages, use_container_width=True)
    with col_target:
        st.selectbox("Translate to", options=target_options, key="target_lang_name")

    st.write("")

    # ---- Input / Output panels --------------------------------------------
    col_input, col_output = st.columns(2)

    with col_input:
        with st.container(border=True):
            st.markdown("<div class='glass-card__title'>✍️ Original Text</div>", unsafe_allow_html=True)
            st.text_area(
                "Enter text to translate",
                key="input_text",
                height=200,
                placeholder="Type or paste text here... (up to 5000 characters)",
                label_visibility="collapsed",
            )
            text = st.session_state.get("input_text", "")
            st.markdown(
                f"""
                <div class="metric-row">
                    <span class="metric-pill">🔤 <strong>{count_characters(text)}</strong> characters</span>
                    <span class="metric-pill">📝 <strong>{count_words(text)}</strong> words</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                translate_clicked = st.button("🌐 Translate", type="primary", use_container_width=True)
            with btn_col2:
                st.button("🧹 Clear", on_click=_clear_all, use_container_width=True)

    with col_output:
        with st.container(border=True):
            st.markdown("<div class='glass-card__title'>🎯 Translation</div>", unsafe_allow_html=True)

            if translate_clicked:
                _run_translation()

            # NOTE: intentionally no `key=` here. This box is read-only and
            # always mirrors `output_text`; combining `value=` with a `key`
            # would make Streamlit prefer the (stale) session_state entry
            # over fresh values on subsequent reruns.
            output_text = st.session_state.get("output_text", "")
            st.text_area(
                "Translated text",
                value=output_text,
                height=200,
                disabled=True,
                label_visibility="collapsed",
            )

            meta = st.session_state.get("translation_meta")
            if meta and meta.get("detected"):
                st.markdown(
                    f"<div class='detected-chip'>🧠 Detected: {meta['source_name']}</div>",
                    unsafe_allow_html=True,
                )

            st.markdown(
                f"""
                <div class="metric-row">
                    <span class="metric-pill">🔤 <strong>{count_characters(output_text)}</strong> characters</span>
                    <span class="metric-pill">📝 <strong>{count_words(output_text)}</strong> words</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if output_text:
                _render_output_actions(output_text, meta)


def _run_translation() -> None:
    """Execute a translation request and persist it to history."""
    text = st.session_state.get("input_text", "")
    source_name = st.session_state.get("source_lang_name")
    target_name = st.session_state.get("target_lang_name")

    source_code = "auto" if source_name == "Detect Language (Auto)" else name_to_code(source_name)
    target_code = name_to_code(target_name)

    with st.spinner("🔄 Translating with AI..."):
        try:
            result = translate_text(text, source_code=source_code, target_code=target_code)
        except TranslationError as exc:
            st.session_state["output_text"] = ""
            st.session_state["translation_meta"] = None
            st.markdown(f"<div class='status-banner status-banner--error'>❌ {exc}</div>", unsafe_allow_html=True)
            return

    st.session_state["output_text"] = result.translated_text
    st.session_state["translation_meta"] = {
        "source_code": result.source_code,
        "source_name": result.source_name,
        "target_code": result.target_code,
        "target_name": result.target_name,
        "detected": result.detected,
    }
    st.session_state["audio_bytes"] = None

    entry = HistoryEntry.new(
        source_language=result.source_name,
        target_language=result.target_name,
        original_text=result.original_text,
        translated_text=result.translated_text,
    )
    st.session_state["history"] = _history_manager.add(entry)

    st.markdown(
        "<div class='status-banner status-banner--success'>✅ Translation complete!</div>",
        unsafe_allow_html=True,
    )


def _render_output_actions(output_text: str, meta: dict | None) -> None:
    """Render the copy / speak / download action row under the output panel."""
    action_col1, action_col2, action_col3 = st.columns(3)

    with action_col1:
        render_copy_button(output_text, label="Copy")

    with action_col2:
        target_code = meta.get("target_code") if meta else None
        if target_code and is_tts_supported(target_code):
            if st.button("🔊 Listen", use_container_width=True, key="tts_button"):
                try:
                    with st.spinner("Generating audio..."):
                        audio_bytes = synthesize_speech(output_text, target_code)
                    st.session_state["audio_bytes"] = audio_bytes
                except SpeechSynthesisError as exc:
                    st.markdown(f"<div class='status-banner status-banner--error'>🔇 {exc}</div>", unsafe_allow_html=True)
        else:
            st.button("🔇 Listen", use_container_width=True, disabled=True, help="Not supported for this language")

    with action_col3:
        filename = f"translation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        st.download_button(
            "⬇️ Download",
            data=output_text,
            file_name=filename,
            mime="text/plain",
            use_container_width=True,
        )

    if st.session_state.get("audio_bytes"):
        st.audio(st.session_state["audio_bytes"], format="audio/mp3")
