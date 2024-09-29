from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt, QPoint

class TransparentOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.action_points = []
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        for x, y in self.action_points:
            painter.setBrush(QColor(255, 0, 0, 128))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPoint(x, y), 5, 5)

    def update_points(self, points):
        self.action_points = points
        self.update()

def create_overlay(action_points):
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    overlay = TransparentOverlay()
    overlay.update_points(action_points)
    return app, overlay

def update_overlay(overlay, action_points):
    overlay.update_points(action_points)
