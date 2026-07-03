"""Sidebar navigation & settings component."""

from __future__ import annotations

import streamlit as st

from utils.languages import POPULAR_LANGUAGES


def render_sidebar() -> None:
    """Render the sidebar: branding, theme switch, favorites, stats, help.

    Reads and writes directly to `st.session_state` so the rest of the app
    can simply read `st.session_state["theme"]` / `["favorites"]` etc.
    """
    with st.sidebar:
        st.markdown("### 🌐 LinguaAI")
        st.caption("AI Language Translation Tool")
        st.divider()

        # ---- Theme switch ------------------------------------------------
        st.markdown("#### 🎨 Appearance")
        st.radio(
            "Theme",
            options=["dark", "light"],
            format_func=lambda t: "🌙 Dark Mode" if t == "dark" else "☀️ Light Mode",
            key="theme",
            label_visibility="collapsed",
        )

        st.divider()

        # ---- Favorite languages ------------------------------------------
        st.markdown("#### ⭐ Favorite Languages")
        st.caption("Quick-pick shortlist for the target language.")
        st.multiselect(
            "Favorites",
            options=POPULAR_LANGUAGES,
            key="favorites",
            label_visibility="collapsed",
        )

        st.divider()

        # ---- Stats ----------------------------------------------------------
        st.markdown("#### 📊 Session Stats")
        history_count = len(st.session_state.get("history", []))
        col1, col2 = st.columns(2)
        col1.metric("Translations", history_count)
        col2.metric("Favorites", len(st.session_state.get("favorites", [])))

        st.divider()

        # ---- Keyboard shortcuts ----------------------------------------------
        with st.expander("⌨️ Keyboard Shortcuts"):
            st.markdown(
                """
                | Shortcut | Action |
                |---|---|
                | `Ctrl / Cmd + Enter` | Translate |
                | `Ctrl / Cmd + Backspace` | Clear text |
                """
            )

        with st.expander("ℹ️ About"):
            st.markdown(
                """
                **LinguaAI Translator** is an AI-powered translation tool
                built for the **CodeAlpha Artificial Intelligence
                Internship**.

                Built with Streamlit, Google Translate NMT, and gTTS.
                """
            )

        st.markdown(
            "<div class='app-footer'>Crafted with ❤️ · v1.0.0</div>",
            unsafe_allow_html=True,
        )
