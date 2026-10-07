from __future__ import annotations

import pygetwindow as gw
import pyperclip
import psutil


def get_app_context() -> dict:
    app_name = "Desktop"
    window_title = "Janela ativa não detectada"
    selected_text = ""

    try:
        active = gw.getActiveWindow()
        if active is not None:
            title = active.title or ""
            if title:
                app_name = title
                window_title = title
    except Exception:
        pass

    try:
        current = psutil.Process()
        current_name = current.name() or ""
        if current_name:
            app_name = current_name
    except Exception:
        pass

    try:
        selected_text = pyperclip.paste() or ""
    except Exception:
        selected_text = ""

    return {
        "application": app_name,
        "window_title": window_title,
        "language": "python",
        "selected_text": selected_text.strip(),
        "file_path": "",
    }
