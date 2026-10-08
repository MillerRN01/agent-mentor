from __future__ import annotations

import os
import re
import subprocess
import pygetwindow as gw
import pyperclip
import psutil


def detect_language(filename: str) -> str:
    """Detecta a linguagem de programação baseado na extensão do arquivo."""
    extension_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'react',
        '.tsx': 'react',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.rb': 'ruby',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.sql': 'sql',
        '.sh': 'bash',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.json': 'json',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yaml',
    }
    
    _, ext = os.path.splitext(filename.lower())
    return extension_map.get(ext, 'unknown')


def get_active_window_title() -> str:
    """Retorna o título da janela ativa."""
    try:
        active = gw.getActiveWindow()
        if active is not None:
            return active.title or "Sem título"
    except Exception:
        pass
    return "Sem janela ativa"


def get_active_process() -> str:
    """Retorna o nome do processo ativo."""
    try:
        current = psutil.Process()
        return current.name() or "Desconhecido"
    except Exception:
        pass
    return "Desconhecido"


def get_editor_from_window() -> str | None:
    """Detecta qual editor/IDE está aberto analisando a janela ativa."""
    try:
        window_title = get_active_window_title().lower()
        
        editors = {
            'vs code': 'VS Code',
            'visual studio code': 'VS Code',
            'pycharm': 'PyCharm',
            'intellij': 'IntelliJ',
            'sublime': 'Sublime Text',
            'atom': 'Atom',
            'vim': 'Vim',
            'neovim': 'Neovim',
            'notepad++': 'Notepad++',
            'notepad': 'Notepad',
            'vscode': 'VS Code',
        }
        
        for keyword, editor in editors.items():
            if keyword in window_title:
                return editor
    except Exception:
        pass
    return None


def extract_filename_from_window() -> str | None:
    """Tenta extrair o nome do arquivo da janela ativa."""
    try:
        window_title = get_active_window_title()
        
        # Padrão: "nome-arquivo.ext - Programa"
        match = re.search(r'([\w\-_\.]+\.[a-zA-Z0-9]+)', window_title)
        if match:
            return match.group(1)
        
        # Se houver - no título, tira a parte depois
        if ' - ' in window_title:
            filename = window_title.split(' - ')[0].strip()
            if '.' in filename:
                return filename
    except Exception:
        pass
    return None


def get_selected_text() -> str:
    """Retorna o texto do clipboard (simulando texto selecionado)."""
    try:
        text = pyperclip.paste() or ""
        # Limita a 1000 caracteres para evitar overhead
        return text[:1000].strip()
    except Exception:
        return ""


def get_app_context() -> dict:
    """Monta o contexto completo do ambiente."""
    
    window_title = get_active_window_title()
    process_name = get_active_process()
    editor = get_editor_from_window()
    filename = extract_filename_from_window()
    selected_text = get_selected_text()
    language = detect_language(filename) if filename else "unknown"
    
    context = {
        "application": process_name,
        "window_title": window_title,
        "editor": editor or "Desconhecido",
        "filename": filename or "Sem arquivo",
        "language": language,
        "selected_text": selected_text,
        "file_path": "",
    }
    
    return context
