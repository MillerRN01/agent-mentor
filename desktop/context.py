from __future__ import annotations

import os
import re
from typing import Optional

import psutil
import pygetwindow as gw
import pyperclip


def detect_language(filename: str | None) -> str:
    if not filename:
        return "unknown"

    ext_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript-react',
        '.jsx': 'javascript-react',
        '.java': 'java',
        '.cs': 'csharp',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c': 'c',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.rb': 'ruby',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.sql': 'sql',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.md': 'markdown',
        '.sh': 'bash',
        '.ps1': 'powershell',
        '.bat': 'batch',
        '.txt': 'text',
    }

    _, ext = os.path.splitext(filename.lower())
    return ext_map.get(ext, 'unknown')


def get_active_window_title() -> str:
    try:
        active = gw.getActiveWindow()
        if active is not None and active.title:
            return active.title.strip()
    except Exception:
        pass
    return "Janela ativa não detectada"


def get_active_process_name() -> str:
    try:
        process = psutil.Process()
        name = process.name()
        if name:
            return name
    except Exception:
        pass
    return "Desktop"


def detect_editor_from_title(title: str) -> str | None:
    normalized = title.lower()
    editors = {
        'visual studio code': 'VS Code',
        'vscode': 'VS Code',
        'code -': 'VS Code',
        'pycharm': 'PyCharm',
        'intellij idea': 'IntelliJ IDEA',
        'sublime text': 'Sublime Text',
        'notepad++': 'Notepad++',
        'notepad': 'Notepad',
        'vim': 'Vim',
        'neovim': 'Neovim',
        'atom': 'Atom',
        'cursor': 'Cursor',
    }

    for key, value in editors.items():
        if key in normalized:
            return value

    return None


def extract_filename_from_window_title(title: str) -> str | None:
    patterns = [
        r"([A-Za-z0-9_\-.]+\.(?:py|js|ts|tsx|jsx|java|cs|cpp|c|go|rs|php|rb|swift|kt|sql|html|css|scss|json|yaml|yml|md|sh|ps1|bat|txt))",
        r"([A-Za-z0-9_\-.]+\.[A-Za-z0-9]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            return match.group(1)

    if ' - ' in title:
        candidate = title.split(' - ')[0].strip()
        if '.' in candidate:
            return candidate

    return None


def find_file_path(filename: Optional[str]) -> str:
    if not filename:
        return ""

    candidates = []
    candidates.append(filename)
    candidates.append(os.path.abspath(filename))

    for root in [
        os.getcwd(),
        os.path.expanduser('~'),
        'C:/',
        'D:/',
        'E:/',
    ]:
        candidates.append(os.path.join(root, filename))

    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    return ""


def get_selected_text() -> str:
    try:
        text = pyperclip.paste() or ""
        return text.strip()[:2000]
    except Exception:
        return ""


def get_app_context() -> dict:
    window_title = get_active_window_title()
    process_name = get_active_process_name()
    editor = detect_editor_from_title(window_title)
    filename = extract_filename_from_window_title(window_title)
    file_path = find_file_path(filename)
    selected_text = get_selected_text()

    return {
        "application": process_name,
        "window_title": window_title,
        "editor": editor or "Desconhecido",
        "filename": filename or "Sem arquivo",
        "language": detect_language(filename),
        "selected_text": selected_text,
        "file_path": file_path,
    }
