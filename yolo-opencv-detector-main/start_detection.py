import numpy as np
import win32gui, win32ui, win32con
from PIL import Image
from time import sleep
import cv2 as cv
import os
import random
import time
import mss
import math
import pydirectinput
import time
import pyautogui  
from pynput.mouse import Controller as MouseController

mouse_controller = MouseController()

class WindowCapture:
    w = 0
    h = 0
    hwnd = None

    def __init__(self, window_name):
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]  # Monitor 1 is usually the primary monitor
        self.w = self.monitor['width']
        self.h = self.monitor['height']

    def get_screenshot(self):
        screenshot = self.sct.grab(self.monitor)
        img = np.array(screenshot)
        img = img[..., :3]  # Drop alpha channel if necessary
        img = cv.cvtColor(img, cv.COLOR_RGB2BGR)  # Convert RGB to BGR for OpenCV
        img = np.ascontiguousarray(img)  # Ensure contiguous memory layout
        return img

    def get_window_size(self):
        return (self.w, self.h)

class ImageProcessor:
    W = 0
    H = 0
    net = None
    ln = None
    classes = {}
    colors = []

    def __init__(self, img_size, cfg_file, weights_file):
        np.random.seed(42)
        self.net = cv.dnn.readNetFromDarknet(cfg_file, weights_file)
        self.net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)
        self.ln = [self.net.getLayerNames()[i - 1] for i in self.net.getUnconnectedOutLayers().flatten()]

        self.W, self.H = img_size
        
        with open('yolov4-tiny/obj.names', 'r') as file:
            lines = file.readlines()
        for i, line in enumerate(lines):
            self.classes[i] = line.strip()
        
        # Colors for different classes
        self.colors = [
            (0, 0, 255), 
            (0, 255, 0), 
            (255, 0, 0), 
            (255, 255, 0), 
            (255, 0, 255), 
            (0, 255, 255)
        ]

    def proccess_image(self, img):
        blob = cv.dnn.blobFromImage(img, 1/255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward(self.ln)
        outputs = np.vstack(outputs)
        
        coordinates = self.get_coordinates(outputs, 0.5)
        self.draw_identified_objects(img, coordinates)
        return coordinates

    def get_coordinates(self, outputs, conf):
        boxes = []
        confidences = []
        classIDs = []

        for output in outputs:
            scores = output[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]
            if confidence > conf:
                x, y, w, h = output[:4] * np.array([self.W, self.H, self.W, self.H])
                p0 = int(x - w//2), int(y - h//2)
                boxes.append([*p0, int(w), int(h)])
                confidences.append(float(confidence))
                classIDs.append(classID)

        indices = cv.dnn.NMSBoxes(boxes, confidences, conf, conf-0.1)

        if len(indices) == 0:
            return []

        coordinates = []
        for i in indices.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])
            coordinates.append({'x': x, 'y': y, 'w': w, 'h': h, 'class': classIDs[i], 'class_name': self.classes[classIDs[i]]})
        return coordinates

    def draw_identified_objects(self, img, coordinates):
        for coordinate in coordinates:
            x = coordinate['x']
            y = coordinate['y']
            w = coordinate['w']
            h = coordinate['h']
            classID = coordinate['class']
            color = self.colors[classID]
            
            print(f"Drawing rectangle at x: {x}, y: {y}, width: {w}, height: {h}")

            cv.rectangle(img, (x, y), (x + w, y + h), color, 2)
            cv.putText(img, self.classes[classID], (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv.imshow('window', img)



    
# ================================ Automating Character Movements ======================================



def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def calculate_movement_direction(character_x, character_y, target_x, target_y):
    dx = target_x - character_x
    dy = target_y - character_y
    
    if dx > 0 and dy > 0:
        return "move down-right"
    elif dx > 0 and dy > 0 and abs(dx) < 30:
        return "move down"
    elif dx > 0 and dy < 0:
        return "move up-right"
    elif dx > 0 and dy < 0 and abs(dx) < 30:
        return "move up"
    elif dx < 0 and dy > 0:
        return "move down-left"
    if dx < 0 and dy > 0 and abs(dx) < 30:
        return "move down"    
    elif dx < 0 and dy < 0:
        return "move up-left"
    elif dx < 0 and dy < 0 and abs(dx) < 30:
        return "move up"    
    elif dx > 0:
        return "move right"
    elif dx < 0:
        return "move left"
    elif dy > 0:
        return "move down"
    elif dy < 0:
        return "move up"
    else:
        return "stay"

def move_character(direction, movement_time):
    
    if direction == "move up":
        pydirectinput.keyDown("shift")
        pydirectinput.keyDown("w")
        time.sleep(movement_time)
        pydirectinput.keyUp("w")
        pydirectinput.keyUp("shift")
    elif direction == "move down":
        pydirectinput.keyDown("s")
        time.sleep(movement_time)
        pydirectinput.keyUp("s")
    elif direction == "move left":
        pydirectinput.keyDown("a")
        time.sleep(movement_time)
        pydirectinput.keyUp("a")
    elif direction == "move right":
        pydirectinput.keyDown("d")
        time.sleep(movement_time)
        pydirectinput.keyUp("d")
    elif direction == "move up-right":
        pydirectinput.keyDown("w")
        pydirectinput.keyDown("d")
        time.sleep(movement_time)
        pydirectinput.keyUp("w")
        pydirectinput.keyUp("d")
    elif direction == "move up-left":
        pydirectinput.keyDown("w")
        pydirectinput.keyDown("a")
        time.sleep(movement_time)
        pydirectinput.keyUp("w")
        pydirectinput.keyUp("a")
    elif direction == "move down-right":
        pydirectinput.keyDown("s")
        pydirectinput.keyDown("d")
        time.sleep(movement_time)
        pydirectinput.keyUp("s")
        pydirectinput.keyUp("d")
    elif direction == "move down-left":
        pydirectinput.keyDown("s")
        pydirectinput.keyDown("a")
        time.sleep(movement_time)
        pydirectinput.keyUp("s")
        pydirectinput.keyUp("a")

        

    

def attack_enemy():
    
    for i in range(3):

        pydirectinput.click()
        time.sleep(0.1)
        pydirectinput.click()
        
        pydirectinput.click(button='right')
        time.sleep(1)
        pydirectinput.click(button='right')
       

        pydirectinput.click()
        time.sleep(0.1)
        pydirectinput.click()

        pydirectinput.keyDown('f')
        time.sleep(0.1)
        # pydirectinput.click(button='right')
        pydirectinput.keyUp('f')

        pydirectinput.click()
        time.sleep(0.1)
        pydirectinput.click()


previuos_nearest_target = None
no_target_view_count = 0
def main():
    global previuos_nearest_target, no_target_view_count
    window_name = "Black Desert on GeForce NOW - Google Chrome"
    cfg_file_name = "./yolov4-tiny/yolov4-tiny-custom.cfg"
    weights_file_name = "yolov4-tiny-custom_last.weights"

    # Initialize character position and window capture
    character_x, character_y = 1920 // 2, 1080 // 2
    wincap = WindowCapture(window_name)
    improc = ImageProcessor(wincap.get_window_size(), cfg_file_name, weights_file_name)

    

    while True:
        ss = wincap.get_screenshot()
        
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            break


        # Rotating the camera 90 deg horizontally first:
        angle_diff = 90
        while angle_diff > 180:
            angle_diff -= 360
        while angle_diff < -180:
            angle_diff += 360

        x_shift_scale_factor = 2.0  # Adjust the scale factor based on your needs
        x_movement_total = int(angle_diff * x_shift_scale_factor)
        x_movement_step = 50  # Smaller steps for smoother camera movement    

        screen_width, screen_height = pyautogui.size()
        center_x, center_y = screen_width // 2, screen_height // 2
        pyautogui.moveTo(center_x, center_y)

        # Perform incremental camera movement based on the calculated angle difference
        remaining_movement = abs(x_movement_total)
        movement_direction = 1 if x_movement_total > 0 else -1

        while remaining_movement > 0:
            move_step = min(x_movement_step, remaining_movement) * movement_direction
            pydirectinput.moveRel(
                move_step, 0, duration=0.5
            )  # Simulate horizontal mouse movement
            remaining_movement -= abs(move_step)

        coordinates = improc.proccess_image(ss)

        
        if not coordinates:
            no_target_view_count += 1
            print(f"No targets detected. No_Count: {no_target_view_count}")
            # pydirectinput.moveRel(90, duration=0.1)
            x, y = pyautogui.position()  
            print(f"Mouse coordinates: X={x}, Y={y}", end='\r')
            if x >= 1900:
                time.sleep(.5)
                mouse_controller.position = (character_x, character_y)

            # If you cant find any target around, try move the character
            if no_target_view_count >= 23:
                pydirectinput.keyDown('w')
                time.sleep(3.5 if no_target_view_count == 23 else .5)
                pydirectinput.keyUp('w')

                time.sleep(.5)
            continue
            
        no_target_view_count = 0

        # Find the nearest target
        nearest_target = None
        min_distance = float('inf')
        

        for coordinate in coordinates:
            print(coordinate)
            target_x = coordinate['x'] + (coordinate['w'] // 2)
            target_y = coordinate['y'] + (coordinate['h'] // 2)
            print(f"target_center: ({target_x, target_y})")
            distance = calculate_distance(character_x, character_y, target_x, target_y)

            if distance < min_distance:
                min_distance = distance
                nearest_target = coordinate
        
        if nearest_target:
            # Calculate direction and time to move towards the nearest target
            nearest_target_center_x = nearest_target['x'] + (coordinate['w'] // 2)
            nearest_target_center_y = nearest_target['y'] + (coordinate['h'] // 2)
            direction = calculate_movement_direction(character_x, character_y, nearest_target_center_x, nearest_target_center_y)
            movement_time = min_distance * 0.003  # Adjust this scaling factor as needed

            print(f"min_distance: {min_distance}, movement_time: {movement_time}")

            print(f"Moving {direction} towards target at ({nearest_target['x']}, {nearest_target['y']})")
            move_character(direction, movement_time)
            time.sleep(.5)
            if previuos_nearest_target == nearest_target:
                print("previous and nearst target matches, start attack...")
            attack_enemy()
            previuos_nearest_target = nearest_target


if __name__ == "__main__":
    main()
