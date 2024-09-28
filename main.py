# mouse.py

import cv2
import numpy as np
import pyautogui
import keyboard
from mss import mss

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

def find_nearest_action_point(image):
    # This is a placeholder function. Implement your OpenCV logic here.
    height, width = image.shape[:2]
    return (width // 2, height // 2)

def main():
    screen_width, screen_height = pyautogui.size()
    step = 50  # Increased step size for faster movement

    print("Hold ALT and use ARROW keys to move the mouse.")
    print("ALT + Insert key for left click.")
    print("ALT + Home key to move to nearest action point.")
    print("Press 'ALT + q' to quit.")

    while True:
        if keyboard.is_pressed('alt'):
            if keyboard.is_pressed('q'):
                break
            elif keyboard.is_pressed('insert'):
                pyautogui.click()
            elif keyboard.is_pressed('home'):
                screen = capture_screen()
                x, y = find_nearest_action_point(screen)
                smooth_move(x, y)
            elif keyboard.is_pressed('up'):
                x, y = pyautogui.position()
                smooth_move(x, max(0, y - step))
            elif keyboard.is_pressed('down'):
                x, y = pyautogui.position()
                smooth_move(x, min(screen_height, y + step))
            elif keyboard.is_pressed('left'):
                x, y = pyautogui.position()
                smooth_move(max(0, x - step), y)
            elif keyboard.is_pressed('right'):
                x, y = pyautogui.position()
                smooth_move(min(screen_width, x + step), y)

        cv2.waitKey(1)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
