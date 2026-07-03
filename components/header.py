"""Hero header component displayed at the top of the app."""

from __future__ import annotations

import streamlit as st


def render_header() -> None:
    """Render the glassmorphism hero banner with title and feature badges."""
    st.markdown(
        """
        <div class="app-hero">
            <div class="app-hero__title">🌐 LinguaAI Translator</div>
            <div class="app-hero__subtitle">
                Enterprise-grade AI language translation, powered by neural machine translation
            </div>
            <div class="app-hero__badges">
                <span class="badge">🚀 150+ Languages</span>
                <span class="badge">🎙️ Text-to-Speech</span>
                <span class="badge">🧠 Auto-Detect</span>
                <span class="badge">⚡ Real-Time</span>
                <span class="badge">🔒 Privacy-First</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
