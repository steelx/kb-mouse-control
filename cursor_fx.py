import ctypes # is used for calling Windows API functions.
import win32gui
import win32con
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer

def enable_cursor_trail(length=5):
    ctypes.windll.user32.SystemParametersInfoW(0x005E, length, None, 0)

def disable_cursor_trail():
    ctypes.windll.user32.SystemParametersInfoW(0x005E, 0, None, 0)

def flash_cursor_position(x, y, duration=0.3, flashes=3):
    indicator = QWidget()
    indicator.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
    indicator.setAttribute(Qt.WA_TranslucentBackground)
    indicator.setStyleSheet("background-color: rgba(255, 0, 0, 128); border-radius: 10px;")
    indicator.setGeometry(x-10, y-10, 20, 20)

    def toggle():
        indicator.setVisible(not indicator.isVisible())

    timer = QTimer()
    timer.timeout.connect(toggle)
    timer.start(int(duration * 1000 / (2 * flashes)))

    indicator.show()
    QTimer.singleShot(int(duration * 1000), indicator.close)
    app.processEvents()

def show_cursor_position(x, y, duration=0.3):
    indicator = QWidget()
    indicator.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
    indicator.setAttribute(Qt.WA_TranslucentBackground)
    indicator.setStyleSheet("background-color: rgba(255, 0, 0, 128); border-radius: 10px;")
    indicator.setGeometry(x-10, y-10, 20, 20)
    indicator.show()
    QTimer.singleShot(int(duration * 1000), indicator.close)
    app.processEvents()
