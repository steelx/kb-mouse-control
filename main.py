import sys
import cv2
import pyautogui
import keyboard
from queue import Queue
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from log_window import LogWindow, get_caps_lock_state
from screen import (
    smooth_move,
    capture_screen,
    find_action_points,
    find_nearest_point_in_direction
)
from overlay import TransparentOverlay

class MainThread(QThread):
    update_overlay_signal = pyqtSignal(list)
    log_signal = pyqtSignal(str)
    quit_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = True

    def run(self):
        screen_width, screen_height = pyautogui.size()
        step = 50
        action_points = []
        last_caps_lock_state = False

        self.log_signal.emit("Mouse Control Started")
        self.log_signal.emit("Hold ALT and use ARROW keys to move the mouse.")
        self.log_signal.emit("Turn Caps Lock ON for action point movement.")
        self.log_signal.emit("ALT + Insert for left click.")
        self.log_signal.emit("ALT + Page Down to refresh action points.")
        self.log_signal.emit("Press 'ALT + q' to quit.")

        while self.running:
            caps_lock_state = get_caps_lock_state()

            if caps_lock_state != last_caps_lock_state:
                if not caps_lock_state:
                    self.update_overlay_signal.emit([])  # Clear overlay
                last_caps_lock_state = caps_lock_state

            if keyboard.is_pressed('alt'):
                if keyboard.is_pressed('q'):
                    self.running = False
                    self.quit_signal.emit()
                    break
                elif keyboard.is_pressed('insert'):
                    pyautogui.click()
                    self.log_signal.emit("Left Click")
                elif keyboard.is_pressed('pagedown'):
                    screen_area = capture_screen()
                    action_points = find_action_points(screen_area)
                    self.log_signal.emit(f"Found {len(action_points)} action points")
                    self.update_overlay_signal.emit(action_points)
                elif keyboard.is_pressed('up') or keyboard.is_pressed('down') or \
                    keyboard.is_pressed('left') or keyboard.is_pressed('right'):

                    current_pos = pyautogui.position()
                    direction = None
                    if keyboard.is_pressed('up'): direction = 'up'
                    elif keyboard.is_pressed('down'): direction = 'down'
                    elif keyboard.is_pressed('left'): direction = 'left'
                    elif keyboard.is_pressed('right'): direction = 'right'

                    if caps_lock_state and action_points:
                        nearest_point = find_nearest_point_in_direction(current_pos, action_points, direction)
                        if nearest_point:
                            pyautogui.moveTo(*nearest_point)
                            self.log_signal.emit(f"Teleported to action point: {nearest_point}")
                    else:
                        x, y = current_pos
                        if direction == 'up': smooth_move(x, max(0, y - step))
                        elif direction == 'down': smooth_move(x, min(screen_height, y + step))
                        elif direction == 'left': smooth_move(max(0, x - step), y)
                        elif direction == 'right': smooth_move(min(screen_width, x + step), y)
                        self.log_signal.emit(f"Moved {direction}")

                    self.update_overlay_signal.emit(action_points)

            cv2.waitKey(1)

        self.log_signal.emit("Mouse Control Ended")
        self.log_signal.emit("QUIT")
        cv2.destroyAllWindows()

class MainWindow(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.message_queue = Queue()
        self.log_window = LogWindow(self.message_queue)
        self.overlay = None
        self.main_thread = MainThread()
        self.main_thread.update_overlay_signal.connect(self.update_overlay)
        self.main_thread.log_signal.connect(self.log_message)
        self.main_thread.quit_signal.connect(self.quit)
        self.main_thread.start()

        # Use a timer to keep the application running
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: None)
        self.timer.start(100)

    def update_overlay(self, action_points):
        if not action_points:
            if self.overlay:
                self.overlay.hide()
                self.overlay = None
        else:
            if self.overlay is None:
                self.overlay = TransparentOverlay()
            self.overlay.update_points(action_points)
            self.overlay.show()

    def log_message(self, message):
        self.log_window.add_message(message)
    
    def quit(self):
        if self.overlay:
            self.overlay.close()
        self.log_window.root.quit()
        self.log_window.root.destroy()
        super().quit()

if __name__ == "__main__":
    app = MainWindow(sys.argv)
    app.log_window.root.mainloop()
    sys.exit(app.exec_())
