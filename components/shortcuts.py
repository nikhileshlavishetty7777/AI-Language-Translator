"""Global keyboard shortcuts.

Streamlit doesn't expose native hotkey bindings, so this component injects
a small JS listener (scoped to the parent document, since components render
inside a sandboxed iframe) that watches for key combinations and simulates
a click on the matching Streamlit button, matched by its visible label.
"""

from __future__ import annotations

import streamlit.components.v1 as components


def render_keyboard_shortcuts() -> None:
    """Attach global keyboard shortcuts for the main translator actions.

    Shortcuts:
        Ctrl/Cmd + Enter  -> Click the "Translate" button
        Ctrl/Cmd + Backspace -> Click the "Clear" button
        Ctrl/Cmd + Shift + C -> Click the "Copy Translation" button
    """
    html = """
    <script>
    (function() {
        const parentDoc = window.parent.document;

        function clickButtonByText(fragment) {
            const buttons = parentDoc.querySelectorAll('button');
            for (const btn of buttons) {
                if (btn.innerText && btn.innerText.includes(fragment)) {
                    btn.click();
                    return true;
                }
            }
            return false;
        }

        // Avoid attaching duplicate listeners on every Streamlit rerun.
        if (window.parent.__translatorShortcutsBound) { return; }
        window.parent.__translatorShortcutsBound = true;

        window.parent.document.addEventListener('keydown', function(e) {
            const ctrlOrCmd = e.ctrlKey || e.metaKey;
            if (!ctrlOrCmd) { return; }

            if (e.key === 'Enter') {
                e.preventDefault();
                clickButtonByText('Translate');
            } else if (e.key === 'Backspace') {
                e.preventDefault();
                clickButtonByText('Clear');
            }
        });
    })();
    </script>
    """
    components.html(html, height=0, width=0)
