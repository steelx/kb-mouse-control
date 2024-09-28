# mouse.py

import cv2
import numpy as np
import pyautogui
import keyboard

def smooth_move(x, y, speed=20):
    current_x, current_y = pyautogui.position()
    steps = max(abs(x - current_x), abs(y - current_y)) // speed
    for i in range(steps):
        next_x = current_x + (x - current_x) * ((i+1) / steps)
        next_y = current_y + (y - current_y) * ((i+1) / steps)
        pyautogui.moveTo(next_x, next_y)
        cv2.waitKey(1)

def capture_screen():
    screenshot = pyautogui.screenshot()
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

def find_nearest_action_point(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Find the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            return (cx, cy)
    # If no contours found, return center of image
    height, width = image.shape[:2]
    return (width // 2, height // 2)

def main():
    screen_width, screen_height = pyautogui.size()
    step = 50  # Increased step size for faster movement

    print("Hold ALT and use ARROW keys to move the mouse.")
    print("ALT + Insert key for left click.")
    print("ALT + Home key to move to nearest action point.")
    print("Press 'ALT + q' to quit.")

    # Create a blank image to simulate screen capture
    screen = capture_screen()
    nearest_point = find_nearest_action_point(screen)

    while True:
        if keyboard.is_pressed('alt'):
            if keyboard.is_pressed('q'):
                break
            elif keyboard.is_pressed('insert'):
                pyautogui.click()
            elif keyboard.is_pressed('home'):
                # Simulate finding nearest action point
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
