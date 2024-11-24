import pyautogui  
import time  

try:  
    print("Press Ctrl+C to stop.")  
    while True:  
        # Get the current mouse position  
        x, y = pyautogui.position()  
        print(f"Mouse coordinates: X={x}, Y={y}", end='\r')  # Use '\r' to overwrite the line  
        time.sleep(0.1)  # Sleep for a short duration to reduce CPU usage  
except KeyboardInterrupt:  
    print("\nProgram terminated.")