import cv2
import numpy as np
import pyautogui
import keyboard
from mss import mss
from queue import Queue
import threading
from log_window import LogWindow, get_caps_lock_state

def smooth_move(x, y, speed=30):
    current_x, current_y = pyautogui.position()
    steps = max(abs(x - current_x), abs(y - current_y)) // speed
    for i in range(steps):
        next_x = current_x + (x - current_x) * ((i+1) / steps)
        next_y = current_y + (y - current_y) * ((i+1) / steps)
        pyautogui.moveTo(next_x, next_y)
        cv2.waitKey(1)

def capture_screen():
    with mss() as sct:
        monitor = sct.monitors[0]
        sct_img = sct.grab(monitor)
        return np.array(sct_img)

def find_action_points(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, 1, 20,
                               param1=50, param2=30, minRadius=10, maxRadius=40)

    action_points = []
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            action_points.append((i[0], i[1]))

    corners = cv2.goodFeaturesToTrack(gray, 100, 0.01, 10)
    if corners is not None:
        for corner in corners:
            x, y = corner.ravel()
            action_points.append((int(x), int(y)))

    return action_points

def find_nearest_point_in_direction(current_pos, action_points, direction):
    x, y = current_pos
    valid_points = []

    if direction == 'up':
        valid_points = [p for p in action_points if p[1] < y]
    elif direction == 'down':
        valid_points = [p for p in action_points if p[1] > y]
    elif direction == 'left':
        valid_points = [p for p in action_points if p[0] < x]
    elif direction == 'right':
        valid_points = [p for p in action_points if p[0] > x]

    if valid_points:
        return min(valid_points, key=lambda p: ((p[0]-x)**2 + (p[1]-y)**2)**0.5)
    return None

def main(queue):
    screen_width, screen_height = pyautogui.size()
    step = 50  # Step size for incremental movement
    action_points = []

    queue.put("Mouse Control Started")
    queue.put("Hold ALT and use ARROW keys to move the mouse.")
    queue.put("Turn Caps Lock ON for action point movement.")
    queue.put("ALT + Insert for left click.")
    queue.put("ALT + Page Down to refresh action points.")
    queue.put("Press 'ALT + q' to quit.")

    while True:
        if keyboard.is_pressed('alt'):
            if keyboard.is_pressed('q'):
                break
            elif keyboard.is_pressed('insert'):
                pyautogui.click()
                queue.put("Left Click")
            elif keyboard.is_pressed('pagedown'):
                screen = capture_screen()
                action_points = find_action_points(screen)
                queue.put(f"Found {len(action_points)} action points")
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

                if get_caps_lock_state() and action_points:
                    nearest_point = find_nearest_point_in_direction(current_pos, action_points, direction)
                    if nearest_point:
                        smooth_move(*nearest_point)
                        queue.put(f"Moved to action point: {nearest_point}")
                else:
                    x, y = current_pos
                    if direction == 'up':
                        smooth_move(x, max(0, y - step))
                    elif direction == 'down':
                        smooth_move(x, min(screen_height, y + step))
                    elif keyboard.is_pressed('left'):
                        smooth_move(max(0, x - step), y)
                    elif keyboard.is_pressed('right'):
                        smooth_move(min(screen_width, x + step), y)
                    queue.put(f"Moved {direction}")

        cv2.waitKey(1)

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
