from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel
from PyQt5.QtCore import Qt, QTimer
from queue import Empty
import ctypes

def get_caps_lock_state():
    hllDll = ctypes.WinDLL("User32.dll")
    VK_CAPITAL = 0x14
    return hllDll.GetKeyState(VK_CAPITAL)

class LogWindow(QWidget):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self.setWindowTitle("KB Mouse Control")
        self.setGeometry(100, 100, 300, 150)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout()

        self.log_text = QTextEdit(self)
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        self.caps_lock_label = QLabel("Caps Lock: OFF", self)
        layout.addWidget(self.caps_lock_label)

        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(100)

    def add_message(self, message):
        self.queue.put(message)

    def update_log(self, message):
        self.log_text.append(message)
        self.log_text.ensureCursorVisible()
        if self.log_text.document().lineCount() > 5:
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.movePosition(cursor.Down, cursor.KeepAnchor)
            cursor.removeSelectedText()

    def update_caps_lock_state(self):
        if get_caps_lock_state():
            self.caps_lock_label.setText("Caps Lock: ON")
        else:
            self.caps_lock_label.setText("Caps Lock: OFF")

    def update_gui(self):
        try:
            while True:
                message = self.queue.get_nowait()
                if message == "QUIT":
                    self.close()
                    return
                self.update_log(message)
        except Empty:
            pass
        self.update_caps_lock_state()
