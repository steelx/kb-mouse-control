import cv2
import numpy as np
import pyautogui
from mss import mss

def smooth_move(x, y, speed=20):
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
        corner_points = [(int(corner[0][0]), int(corner[0][1])) for corner in corners]
        # Sort corner points by x-coordinate, then by y-coordinate
        corner_points.sort(key=lambda p: (p[0], p[1]))
        action_points.extend(corner_points)

    return action_points

def find_nearest_point_in_direction(current_pos, action_points, direction):
    x, y = current_pos
    valid_points = []

    for point in action_points:
        px, py = point
        if direction == 'up' and py < y:
            valid_points.append(point)
        elif direction == 'down' and py > y:
            valid_points.append(point)
        elif direction == 'left' and px < x:
            valid_points.append(point)
        elif direction == 'right' and px > x:
            valid_points.append(point)

    if not valid_points:
        # If no points in the exact direction, consider points slightly off
        for point in action_points:
            px, py = point
            if direction in ['up', 'down'] and abs(px - x) < 50:
                valid_points.append(point)
            elif direction in ['left', 'right'] and abs(py - y) < 50:
                valid_points.append(point)

    if valid_points:
        return min(valid_points, key=lambda p: ((p[0]-x)**2 + (p[1]-y)**2)**0.5)
    return None
