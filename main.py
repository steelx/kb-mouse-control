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

def find_action_points(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    action_points = []
    for contour in contours:
        if cv2.contourArea(contour) > 100:  # Adjust this threshold as needed
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                action_points.append((cx, cy))
    
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

def main():
    screen_width, screen_height = pyautogui.size()
    action_points = []

    print("Hold ALT and use ARROW keys to move the mouse to nearest action point.")
    print("ALT + Insert key for left click.")
    print("ALT + Page Down to refresh action points.")
    print("Press 'ALT + q' to quit.")

    while True:
        if keyboard.is_pressed('alt'):
            if keyboard.is_pressed('q'):
                break
            elif keyboard.is_pressed('insert'):
                pyautogui.click()
            elif keyboard.is_pressed('pagedown'):
                screen = capture_screen()
                action_points = find_action_points(screen)
                print(f"Found {len(action_points)} action points")
            else:
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
                
                if direction:
                    nearest_point = find_nearest_point_in_direction(current_pos, action_points, direction)
                    if nearest_point:
                        smooth_move(*nearest_point)

        cv2.waitKey(1)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
