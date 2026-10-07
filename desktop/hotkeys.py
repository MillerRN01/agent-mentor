from pynput import keyboard


class GlobalHotkey:
    def __init__(self, on_toggle):
        self._on_toggle = on_toggle
        self._listener = None

    def start(self):
        self._listener = keyboard.GlobalHotKeys({
            "<ctrl>+<alt>+m": self._on_toggle,
        })
        self._listener.start()

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener = None
