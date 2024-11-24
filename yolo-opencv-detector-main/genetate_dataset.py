import numpy as np
import win32gui, win32ui, win32con
from PIL import Image
from time import sleep
import os
import time
import mss

class WindowCapture:
    w = 0
    h = 0
    hwnd = None

    def __init__(self, window_name):
        self.sct = mss.mss()
        self.monitor = self.sct.monitors[1]  # Monitor 1 is usually the primary monitor

            

            

    # def get_screenshot(self):
    #     wDC = win32gui.GetWindowDC(self.hwnd)
    #     dcObj = win32ui.CreateDCFromHandle(wDC)
    #     cDC = dcObj.CreateCompatibleDC()
    #     dataBitMap = win32ui.CreateBitmap()
    #     dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
    #     cDC.SelectObject(dataBitMap)
    #     cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (0, 0), win32con.SRCCOPY)

    #     success = cDC.BitBlt((0, 0), (self.w, self.h), dcObj, (0, 0), win32con.SRCCOPY)
    #     if not success:
    #         print("BitBlt failed.")
    #     else:
    #         print("BitBlt succeed")

    #     signedIntsArray = dataBitMap.GetBitmapBits(True)
    #     img = np.frombuffer(signedIntsArray, dtype='uint8')
    #     img.shape = (self.h, self.w, 4)

    #     dcObj.DeleteDC()
    #     cDC.DeleteDC()
    #     win32gui.ReleaseDC(self.hwnd, wDC)
    #     win32gui.DeleteObject(dataBitMap.GetHandle())

    #     img = img[..., :3]  # Remove the alpha channel
    #     img = np.ascontiguousarray(img)
            
    #     return img


    def get_screenshot(self):
        screenshot = self.sct.grab(self.monitor)
        img = np.array(screenshot)
        img = img[..., :3]  # Drop alpha channel if necessary
        return img


    def generate_image_dataset(self):
        if not os.path.exists("images"):
            os.mkdir("images")
        while(True):
            img = self.get_screenshot()
            im = Image.fromarray(img[..., [2, 1, 0]])
            im.save(f"./images/img_{len(os.listdir('images'))}.jpg")
            time.sleep(0.3)
    
    def get_window_size(self):
        return (self.w, self.h)
    

def main():
    window_name = "Black Desert on GeForce NOW - Google Chrome"

    wincap = WindowCapture(window_name)
    wincap.generate_image_dataset()    


if __name__ == "__main__":
    main()