import sys
import threading

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget
from PIL import Image, ImageDraw
import pystray

from api_client import AgentClient
from context import get_app_context
from hotkeys import GlobalHotkey


class AgentWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agent Mentor")
        self.resize(420, 520)
        self.setMinimumWidth(360)

        self.client = AgentClient("http://localhost:8000")
        self.conversation_id = None

        self.chat_log = QTextEdit()
        self.chat_log.setReadOnly(True)
        self.chat_log.setPlaceholderText("Conversa do Agent Mentor")
        self.chat_log.setStyleSheet(
            """
            QTextEdit {
                background: #f8fafc;
                border: 1px solid #cbd5e1;
                border-radius: 10px;
                padding: 10px;
                font-size: 13px;
            }
            """
        )

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Digite sua mensagem...")
        self.input_box.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self.send_message)

        self.status_label = QLabel("Status: aguardando...")
        self.status_label.setStyleSheet("color: #334155; font-size: 11px;")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Agent Mentor"))
        layout.addWidget(self.chat_log)
        layout.addWidget(self.input_box)
        layout.addWidget(self.send_button)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        self.append_message("Assistente", "Olá! Eu sou o Agent Mentor. Pressione Ctrl + Alt + M para abrir.")

    def append_message(self, who: str, text: str):
        self.chat_log.append(f"{who}: {text}")

    def send_message(self):
        text = self.input_box.text().strip()
        if not text:
            return

        self.input_box.clear()
        self.status_label.setText("Status: enviando...")

        try:
            context = get_app_context()
            result = self.client.chat(
                message=text,
                conversation_id=self.conversation_id,
                context=context,
            )
            self.conversation_id = result.get("conversation_id")
            self.append_message("Você", text)
            self.append_message("Assistente", result.get("response", "Sem resposta"))
            self.status_label.setText("Status: resposta recebida")
        except Exception as exc:  # pragma: no cover
            self.append_message("Assistente", f"Erro: {exc}")
            self.status_label.setText("Status: erro de comunicação")

    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()


def make_icon():
    image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((8, 8, 56, 56), fill=(37, 99, 235), radius=10)
    draw.text((18, 18), "AI", fill=(255, 255, 255))
    return image


def app_exit():
    app.quit()


def create_tray_icon(window: AgentWindow):
    icon = pystray.Icon(
        "agent_mentor",
        make_icon(),
        "Agent Mentor",
        menu=pystray.Menu(
            pystray.MenuItem("Abrir", lambda: window.toggle_visibility()),
            pystray.MenuItem("Sair", lambda: app_exit()),
        ),
    )
    return icon


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AgentWindow()
    tray = create_tray_icon(window)

    hotkey = GlobalHotkey(window.toggle_visibility)
    hotkey.start()

    def tray_loop():
        tray.run()

    threading.Thread(target=tray_loop, daemon=True).start()

    window.show()
    sys.exit(app.exec())
