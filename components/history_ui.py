"""Translation history tab component."""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from utils.history import HistoryManager
from utils.validators import truncate_preview

_history_manager = HistoryManager()


def _clear_history() -> None:
    """Callback: wipe all saved translation history."""
    _history_manager.clear()
    st.session_state["history"] = []


def _reuse_entry(original_text: str, source_language: str, target_language: str) -> None:
    """Callback: load a past entry back into the translator inputs."""
    st.session_state["input_text"] = original_text
    st.session_state["source_lang_name"] = source_language
    st.session_state["target_lang_name"] = target_language
    st.toast("Loaded into the translator — switch to the 🌐 Translate tab.", icon="↺")


def render_history_ui() -> None:
    """Render the full History tab: recent list, table, and CSV export."""
    history = st.session_state.get("history", [])

    if not history:
        st.markdown(
            """
            <div class="history-empty">
                <div style="font-size:2.4rem;">🗂️</div>
                <div style="font-weight:700; font-size:1.05rem; margin-top:0.4rem;">No translations yet</div>
                <div style="opacity:0.75;">Your translation history will appear here.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        st.markdown(f"##### 🕘 {len(history)} saved translation(s)")
    with top_col2:
        st.button("🗑️ Clear History", on_click=_clear_history, use_container_width=True)

    st.write("")
    st.markdown("###### ⏱️ Recent Translations")

    for idx, entry in enumerate(history[:8]):
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            with c1:
                st.markdown(
                    f"**{entry['source_language']} → {entry['target_language']}**"
                    f"&nbsp;&nbsp;<span style='opacity:0.6; font-size:0.8rem;'>{entry['timestamp']}</span>",
                    unsafe_allow_html=True,
                )
                st.caption(f"🔤 {truncate_preview(entry['original_text'], 80)}")
                st.markdown(f"🎯 {truncate_preview(entry['translated_text'], 80)}")
            with c2:
                st.button(
                    "↺ Reuse",
                    key=f"reuse_{idx}_{entry['timestamp']}",
                    use_container_width=True,
                    on_click=_reuse_entry,
                    args=(entry["original_text"], entry["source_language"], entry["target_language"]),
                )

    st.write("")
    st.markdown("###### 📋 Full History Table")
    df = HistoryManager.to_dataframe(history)
    st.dataframe(df, use_container_width=True, hide_index=True)

    csv_bytes = HistoryManager.to_csv_bytes(history)
    st.download_button(
        "⬇️ Export History as CSV",
        data=csv_bytes,
        file_name=f"translation_history_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True,
    )
