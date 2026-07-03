"""Client-side "copy to clipboard" component.

Streamlit apps run server-side, so the `pyperclip` library (also bundled in
this project for completeness / offline scripting use) would only ever copy
text into the *server's* clipboard — useless for a deployed web app. This
component instead uses the browser's native `navigator.clipboard` API via a
tiny embedded HTML/JS snippet, so the copy always happens on the visitor's
own machine.
"""

from __future__ import annotations

import json
import uuid

import streamlit.components.v1 as components


def render_copy_button(text: str, label: str = "Copy Translation") -> None:
    """Render a styled button that copies `text` to the user's clipboard.

    Args:
        text: The text to copy.
        label: Button label.
    """
    if not text:
        return

    safe_text = json.dumps(text)  # Safely escapes quotes/newlines for JS.
    element_id = f"copy-btn-{uuid.uuid4().hex[:8]}"

    html = f"""
    <div style="width:100%;">
        <button id="{element_id}" style="
            width:100%;
            padding:0.55rem 1rem;
            border-radius:12px;
            border:1px solid rgba(255,255,255,0.18);
            background:rgba(255,255,255,0.10);
            color:#f5f6fa;
            font-weight:600;
            font-size:0.92rem;
            cursor:pointer;
            font-family:'Segoe UI',sans-serif;
            transition: all 0.2s ease;
        "
        onmouseover="this.style.transform='translateY(-2px)'"
        onmouseout="this.style.transform='translateY(0)'"
        onclick="
            navigator.clipboard.writeText({safe_text}).then(() => {{
                const btn = document.getElementById('{element_id}');
                const original = btn.innerText;
                btn.innerText = '✅ Copied!';
                setTimeout(() => {{ btn.innerText = original; }}, 1500);
            }});
        ">
            📋 {label}
        </button>
    </div>
    """
    components.html(html, height=52)
