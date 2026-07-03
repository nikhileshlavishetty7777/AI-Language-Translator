"""Theme engine.

Loads the structural stylesheet from `assets/style.css` (which is written
entirely against CSS custom properties) and layers a small variable
override block on top, depending on the active theme. This keeps the bulk
of the CSS theme-agnostic and makes adding new themes trivial.
"""

from __future__ import annotations

from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
BASE_STYLESHEET = ASSETS_DIR / "style.css"

# Dark is the default palette already baked into style.css's :root block,
# so only the Light theme needs an explicit override here.
_LIGHT_OVERRIDES = """
:root {
    --bg-gradient-1: #eef1ff;
    --bg-gradient-2: #dce8ff;
    --bg-gradient-3: #f7f4ff;
    --glass-bg: rgba(255, 255, 255, 0.55);
    --glass-bg-strong: rgba(255, 255, 255, 0.75);
    --glass-border: rgba(30, 30, 60, 0.12);
    --text-primary: #201f38;
    --text-secondary: #55597a;
    --accent-1: #6d4de6;
    --accent-2: #17a672;
    --accent-gradient: linear-gradient(135deg, #6d4de6 0%, #17a672 100%);
    --shadow-color: rgba(90, 90, 140, 0.18);
    --success: #17a672;
    --error: #d63a5c;
    --warning: #c98a12;
}
"""


def load_theme_css(theme: str) -> str:
    """Return the complete `<style>` payload for the given theme name.

    Args:
        theme: Either ``"dark"`` or ``"light"``.
    """
    base_css = BASE_STYLESHEET.read_text(encoding="utf-8")
    if theme == "light":
        return f"<style>{base_css}\n{_LIGHT_OVERRIDES}</style>"
    return f"<style>{base_css}</style>"
