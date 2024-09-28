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
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Use Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Find the largest contour
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        # Get the center of the largest contour
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            return (cx, cy)

    # If no contours found, return the center of the image
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
            elif keyboard.is_pressed('pagedown'):
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
