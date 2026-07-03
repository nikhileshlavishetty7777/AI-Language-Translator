"""LinguaAI Translator — AI-Powered Language Translation Tool.

Entry point for the Streamlit application. Responsible only for
orchestration: page configuration, session-state bootstrapping, theme
injection, and wiring together the presentation components. All business
logic lives in `utils/`, all rendering logic lives in `components/`.

Author: Nikhilesh
Project: CodeAlpha Artificial Intelligence Internship — Task: AI Language
Translation Tool.
"""

from __future__ import annotations

import streamlit as st

from components.header import render_header
from components.history_ui import render_history_ui
from components.shortcuts import render_keyboard_shortcuts
from components.sidebar import render_sidebar
from components.translator_ui import render_translator_ui
from utils.history import HistoryManager
from utils.theme import load_theme_css

APP_TITLE = "LinguaAI Translator"
APP_ICON = "🌐"


def configure_page() -> None:
    """Configure Streamlit's page-level metadata and layout."""
    st.set_page_config(
        page_title=f"{APP_TITLE} | AI Language Translation",
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get Help": None,
            "Report a bug": None,
            "About": (
                "**LinguaAI Translator** — an AI-powered language translation tool "
                "built for the CodeAlpha Artificial Intelligence Internship."
            ),
        },
    )


def init_session_state() -> None:
    """Initialise every `st.session_state` key the app depends on.

    Centralising defaults here means every component can safely assume
    these keys already exist, instead of littering `.get(..., default)`
    calls throughout the UI layer.
    """
    defaults = {
        "theme": "dark",
        "favorites": [],
        "input_text": "",
        "output_text": "",
        "translation_meta": None,
        "source_lang_name": "Detect Language (Auto)",
        "target_lang_name": "English",
        "audio_bytes": None,
        "history": None,  # Lazily loaded from disk below.
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if st.session_state["history"] is None:
        st.session_state["history"] = HistoryManager().load()


def inject_theme() -> None:
    """Inject the active theme's CSS into the page."""
    st.markdown(load_theme_css(st.session_state["theme"]), unsafe_allow_html=True)


def render_footer() -> None:
    """Render the closing footer with attribution and links."""
    st.markdown(
        """
        <div class="app-footer">
            Built with ❤️ using Streamlit &amp; Google Neural Machine Translation ·
            <a href="https://github.com" target="_blank">View on GitHub</a> ·
            CodeAlpha AI Internship Project
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """Application entry point."""
    configure_page()
    init_session_state()
    inject_theme()
    render_keyboard_shortcuts()

    render_sidebar()
    render_header()

    tab_translate, tab_history = st.tabs(["🌐 Translate", "🕘 History"])

    with tab_translate:
        render_translator_ui()

    with tab_history:
        render_history_ui()

    render_footer()


if __name__ == "__main__":
    main()
