import sys
import threading

from PIL import Image, ImageDraw
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QTextEdit,
)
import pyperclip
import pystray

from api_client import AgentClient
from context import get_app_context
from hotkeys import GlobalHotkey


class SuggestionBubble(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(260, 110)

        self.frame = QFrame(self)
        self.frame.setStyleSheet(
            """
            QFrame {
                background: rgba(15, 23, 42, 0.96);
                border: 1px solid rgba(148, 163, 184, 0.35);
                border-radius: 14px;
                color: white;
            }
            """
        )

        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        self.label = QLabel("💡 Dica rápida")
        self.label.setStyleSheet(
            """
            QLabel {
                color: #e2e8f0;
                font-weight: 700;
                font-size: 12px;
            }
            """
        )

        self.message = QLabel("Posso explicar, revisar ou corrigir algo para você.")
        self.message.setWordWrap(True)
        self.message.setStyleSheet(
            """
            QLabel {
                color: #dbeafe;
                font-size: 11px;
            }
            """
        )

        buttons = QHBoxLayout()
        self.use_btn = QPushButton("Usar")
        self.use_btn.clicked.connect(self.parent.show_main_window)
        self.use_btn.setStyleSheet(
            """
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 7px 10px;
                font-weight: 700;
            }
            """
        )

        self.close_btn = QPushButton("✕")
        self.close_btn.clicked.connect(self.hide)
        self.close_btn.setStyleSheet(
            """
            QPushButton {
                background: rgba(148, 163, 184, 0.20);
                color: #e2e8f0;
                border: none;
                border-radius: 8px;
                padding: 7px 10px;
                font-weight: 700;
            }
            """
        )

        buttons.addWidget(self.use_btn)
        buttons.addWidget(self.close_btn)

        layout.addWidget(self.label)
        layout.addWidget(self.message)
        layout.addLayout(buttons)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.frame)

    def position_in_corner(self):
        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.right() - self.width() - 30
        y = screen.bottom() - self.height() - 30
        self.move(x, y)


class AgentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agent Mentor")
        self.resize(420, 520)
        self.setMinimumWidth(360)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.client = AgentClient("http://localhost:8000")
        self.conversation_id = None
        self.last_response = ""
        self.minimized = False

        self.main_frame = QFrame(self)
        self.main_frame.setStyleSheet(
            """
            QFrame {
                background: rgba(15, 23, 42, 0.98);
                border: 1px solid rgba(148, 163, 184, 0.35);
                border-radius: 12px;
                color: white;
            }
            """
        )

        self.main_layout = QVBoxLayout(self.main_frame)
        self.main_layout.setContentsMargins(14, 14, 14, 14)
        self.main_layout.setSpacing(10)

        self.header_layout = QHBoxLayout()
        self.header_layout.setSpacing(8)

        self.header = QLabel("🤖 Agent Mentor")
        self.header.setStyleSheet(
            """
            QLabel {
                color: #e2e8f0;
                font-size: 16px;
                font-weight: 700;
            }
            """
        )

        self.btn_minimize = QPushButton("−")
        self.btn_minimize.setMaximumWidth(30)
        self.btn_minimize.clicked.connect(self.showMinimized)

        self.btn_maximize = QPushButton("□")
        self.btn_maximize.setMaximumWidth(30)
        self.btn_maximize.clicked.connect(self.toggle_maximize)

        self.btn_close = QPushButton("✕")
        self.btn_close.setMaximumWidth(30)
        self.btn_close.clicked.connect(self.hide)

        for btn in [self.btn_minimize, self.btn_maximize, self.btn_close]:
            btn.setStyleSheet(
                """
                QPushButton {
                    background: rgba(30, 41, 59, 0.8);
                    color: #e2e8f0;
                    border: 1px solid rgba(148, 163, 184, 0.25);
                    border-radius: 7px;
                    font-weight: 700;
                    padding: 4px;
                }
                QPushButton:hover {
                    background: rgba(30, 41, 59, 1.0);
                    border: 1px solid rgba(148, 163, 184, 0.45);
                }
                """
            )

        self.header_layout.addWidget(self.header)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.btn_minimize)
        self.header_layout.addWidget(self.btn_maximize)
        self.header_layout.addWidget(self.btn_close)

        self.status = QLabel("Pronto para ajudar")
        self.status.setStyleSheet(
            """
            QLabel {
                color: #93c5fd;
                font-size: 11px;
                letter-spacing: 0.08em;
            }
            """
        )

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("Sua conversa aparece aqui...")
        self.output.setStyleSheet(
            """
            QTextEdit {
                background: rgba(15, 23, 42, 0.6);
                border: 1px solid rgba(148, 163, 184, 0.20);
                border-radius: 10px;
                color: #e2e8f0;
                font-size: 12px;
                padding: 8px;
            }
            """
        )

        self.input = QLineEdit()
        self.input.setPlaceholderText("Digite sua dúvida ou peça ajuda...")
        self.input.setStyleSheet(
            """
            QLineEdit {
                background: rgba(30, 41, 59, 0.8);
                border: 1px solid rgba(148, 163, 184, 0.25);
                border-radius: 10px;
                color: white;
                padding: 10px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(37, 99, 235, 0.5);
            }
            """
        )
        self.input.returnPressed.connect(self.send_message)

        self.actions = QHBoxLayout()
        self.actions.setSpacing(8)

        self.btn_explain = QPushButton("Explicar")
        self.btn_explain.clicked.connect(lambda: self.quick_action("explicar"))

        self.btn_review = QPushButton("Revisar")
        self.btn_review.clicked.connect(lambda: self.quick_action("revisar"))

        self.btn_fix = QPushButton("Corrigir")
        self.btn_fix.clicked.connect(lambda: self.quick_action("corrigir"))

        self.btn_copy = QPushButton("Copiar")
        self.btn_copy.clicked.connect(self.copy_last_response)

        self.btn_send = QPushButton("Enviar")
        self.btn_send.clicked.connect(self.send_message)

        for btn in [self.btn_explain, self.btn_review, self.btn_fix, self.btn_copy]:
            btn.setStyleSheet(
                """
                QPushButton {
                    background: #2563eb;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-weight: 700;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background: #1d4ed8;
                }
                """
            )

        self.btn_send.setStyleSheet(
            """
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 14px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #059669;
            }
            """
        )

        self.actions.addWidget(self.btn_explain)
        self.actions.addWidget(self.btn_review)
        self.actions.addWidget(self.btn_fix)
        self.actions.addWidget(self.btn_copy)

        self.main_layout.addLayout(self.header_layout)
        self.main_layout.addWidget(self.status)
        self.main_layout.addWidget(self.output)
        self.main_layout.addWidget(self.input)
        self.main_layout.addLayout(self.actions)
        self.main_layout.addWidget(self.btn_send)

        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(self.main_frame)

        self.suggestion_bubble = SuggestionBubble(self)
        self.suggestion_bubble.position_in_corner()
        self.suggestion_bubble.hide()

        self.show_prompt()

    def show_prompt(self):
        self.output.append("💡 Dica: pressione Ctrl + Alt + M para abrir/fechar.")
        self.output.append("Você pode pedir explicação, revisão ou correção de código.")

    def quick_action(self, action: str):
        action_map = {
            "explicar": "Explique este trecho em linguagem simples e útil para programação.",
            "revisar": "Revise este código e diga se existem problemas, riscos ou melhorias.",
            "corrigir": "Identifique o erro e sugira uma correção clara e prática.",
        }
        text = action_map.get(action, "Ajude-me com isso.")
        self.input.setText(text)
        self.send_message()

    def copy_last_response(self):
        if self.last_response.strip():
            pyperclip.copy(self.last_response)
            self.status.setText("✓ Resposta copiada!")

    def send_message(self):
        text = self.input.text().strip()
        if not text:
            return

        self.input.clear()
        self.status.setText("⏳ Enviando...")

        try:
            context = get_app_context()
            result = self.client.chat(
                message=text,
                conversation_id=self.conversation_id,
                context=context,
            )
            self.conversation_id = result.get("conversation_id")
            response = result.get("response", "Sem resposta")
            self.last_response = response

            self.output.append(f"\n📝 Você: {text}")
            self.output.append(f"\n🤖 Agent: {response}")
            self.status.setText("✓ Pronto")
        except Exception as exc:
            self.output.append(f"\n❌ Erro: {exc}")
            self.status.setText("⚠ Erro de comunicação")

    def show_main_window(self):
        self.show()
        self.raise_()
        self.activateWindow()
        self.suggestion_bubble.hide()

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show_main_window()

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def show_suggestion(self):
        self.suggestion_bubble.position_in_corner()
        self.suggestion_bubble.show()

    def closeEvent(self, event):
        self.hide()
        event.ignore()


def make_icon():
    image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((8, 8, 56, 56), fill=(37, 99, 235), radius=12)
    draw.text((18, 17), "AI", fill=(255, 255, 255))
    return image


def app_exit():
    app.quit()


def create_tray_icon(window: AgentWindow):
    tray = pystray.Icon(
        "agent_mentor",
        make_icon(),
        "Agent Mentor",
        menu=pystray.Menu(
            pystray.MenuItem("Abrir", lambda: window.show_main_window()),
            pystray.MenuItem("Dica", lambda: window.show_suggestion()),
            pystray.MenuItem("Sair", lambda: app_exit()),
        ),
    )
    return tray


class SuggestionBubble(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(260, 110)

        self.frame = QFrame(self)
        self.frame.setStyleSheet(
            """
            QFrame {
                background: rgba(15, 23, 42, 0.96);
                border: 1px solid rgba(148, 163, 184, 0.35);
                border-radius: 14px;
                color: white;
            }
            """
        )

        layout = QVBoxLayout(self.frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        self.label = QLabel("💡 Dica rápida")
        self.label.setStyleSheet(
            """
            QLabel {
                color: #e2e8f0;
                font-weight: 700;
                font-size: 12px;
            }
            """
        )

        self.message = QLabel("Posso explicar, revisar ou corrigir algo para você.")
        self.message.setWordWrap(True)
        self.message.setStyleSheet(
            """
            QLabel {
                color: #dbeafe;
                font-size: 11px;
            }
            """
        )

        buttons = QHBoxLayout()
        self.use_btn = QPushButton("Usar")
        self.use_btn.clicked.connect(self.parent.show_main_window)
        self.use_btn.setStyleSheet(
            """
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 7px 10px;
                font-weight: 700;
            }
            """
        )

        self.close_btn = QPushButton("✕")
        self.close_btn.clicked.connect(self.hide)
        self.close_btn.setStyleSheet(
            """
            QPushButton {
                background: rgba(148, 163, 184, 0.20);
                color: #e2e8f0;
                border: none;
                border-radius: 8px;
                padding: 7px 10px;
                font-weight: 700;
            }
            """
        )

        buttons.addWidget(self.use_btn)
        buttons.addWidget(self.close_btn)

        layout.addWidget(self.label)
        layout.addWidget(self.message)
        layout.addLayout(buttons)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.frame)

    def position_in_corner(self):
        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.right() - self.width() - 30
        y = screen.bottom() - self.height() - 30
        self.move(x, y)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = AgentWindow()
    tray = create_tray_icon(window)

    hotkey = GlobalHotkey(window.toggle_visibility)
    hotkey.start()

    def tray_loop():
        tray.run()

    threading.Thread(target=tray_loop, daemon=True).start()

    window.show()
    window.show_suggestion()
    sys.exit(app.exec())
