import cv2
import numpy as np
import pyautogui
import keyboard
from mss import mss
from queue import Queue
import threading
from log_window import LogWindow, get_caps_lock_state
from screen import (
    smooth_move,
    capture_screen,
    find_action_points,
    find_nearest_point_in_direction
)
from overlay import (
    create_overlay,
    update_overlay
)

from PyQt5.QtWidgets import QApplication

def main(queue):
    screen_width, screen_height = pyautogui.size()
    step = 50  # Step size for incremental movement
    action_points = []
    visible_area = (0, 0, 500, 500)  # Initial visible area (x, y, width, height)

    overlay_app = None
    overlay = None

    queue.put("Mouse Control Started")
    queue.put("Hold ALT and use ARROW keys to move the mouse.")
    queue.put("Turn Caps Lock ON for action point movement.")
    queue.put("ALT + Insert for left click.")
    queue.put("ALT + Page Down to refresh action points.")
    queue.put("Press 'ALT + q' to quit.")

    while True:
        caps_lock_state = get_caps_lock_state()

        if caps_lock_state and overlay is None:
            overlay_app, overlay = create_overlay(action_points)
        elif not caps_lock_state and overlay is not None:
            overlay.hide()
            overlay = None

        if keyboard.is_pressed('alt'):
            if keyboard.is_pressed('q'):
                break
            elif keyboard.is_pressed('insert'):
                pyautogui.click()
                queue.put("Left Click")
            elif keyboard.is_pressed('pagedown'):
                current_x, current_y = pyautogui.position()
                screen_area = capture_screen()
                action_points = find_action_points(screen_area)
                queue.put(f"Found {len(action_points)} action points")
                # Update action points coordinates to screen coordinates
                #action_points = [(x + max(0, current_x - 400), y + max(0, current_y - 400)) for x, y in action_points]
                if overlay:
                    update_overlay(overlay, action_points)
            elif keyboard.is_pressed('up') or keyboard.is_pressed('down') or \
                 keyboard.is_pressed('left') or keyboard.is_pressed('right'):

                current_pos = pyautogui.position()
                direction = None
                if keyboard.is_pressed('up'):
                    direction = 'up'
                elif keyboard.is_pressed('down'):
                    direction = 'down'
                elif keyboard.is_pressed('left'):
                    direction = 'left'
                elif keyboard.is_pressed('right'):
                    direction = 'right'

                if caps_lock_state and action_points:
                    nearest_point = find_nearest_point_in_direction(current_pos, action_points, direction, visible_area)
                    if nearest_point:
                        smooth_move(*nearest_point)
                        queue.put(f"Moved to action point: {nearest_point}")
                else:
                    x, y = current_pos
                    vx, vy, vw, vh = visible_area
                    if direction == 'up':
                        smooth_move(x, max(vy, y - step))
                    elif direction == 'down':
                        smooth_move(x, min(vy + vh, y + step))
                    elif keyboard.is_pressed('left'):
                        smooth_move(max(vx, x - step), y)
                    elif keyboard.is_pressed('right'):
                        smooth_move(min(vx + vw, x + step), y)
                    queue.put(f"Moved {direction}")

                # Update visible area based on current mouse position
                x, y = pyautogui.position()
                visible_area = (max(0, x - 250), max(0, y - 250), 500, 500)

                if overlay is not None:
                    update_overlay(overlay, action_points)

        cv2.waitKey(1)

    if overlay is not None:
        overlay.hide()

    queue.put("Mouse Control Ended")
    queue.put("QUIT")
    cv2.destroyAllWindows()

if __name__ == "__main__":
    message_queue = Queue()
    log_window = LogWindow(message_queue)
    # Run the main function in a separate thread
    main_thread = threading.Thread(target=main, args=(message_queue,))
    main_thread.start()
    # Run the GUI in the main thread
    log_window.root.mainloop()
    # Wait for the main thread to finish
    main_thread.join()
