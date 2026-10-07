import psutil


def get_app_context() -> dict:
    try:
        process = psutil.Process()
        app_name = process.name()
    except Exception:
        app_name = "Desktop"

    context = {
        "application": app_name,
        "window_title": "Janela ativa não detectada",
        "language": "python",
        "selected_text": "",
        "file_path": "",
    }

    return context
