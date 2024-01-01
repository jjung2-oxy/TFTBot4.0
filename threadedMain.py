# threadedMain.py
import threading
import time

import numpy as np
from mss import mss
from PIL import Image, ImageGrab
from ultralytics import YOLO

from listener import KeyboardListener


class ThreadedMain:
    def __init__(self, update_overlay_callback):
        self.model = YOLO('weights/DEPLOY.pt')  # Load YOLO model
        self.update_overlay_callback = update_overlay_callback
        self.running = True
        self.keyboard_listener = KeyboardListener(self.doNothing)

    def run(self):
        listener_thread = threading.Thread(target=self.keyboard_listener.start_listener)
        listener_thread.start()
        self.process_frames()

    def stop_listener(self):
        self.keyboard_listener.stop_listener()
        self.running = False

    def process_frames(self):
        sct = mss()
        monitor = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
        while self.running:
            sct_img = sct.grab(monitor)
            frame = np.array(Image.frombytes('RGB', (sct_img.width, sct_img.height), sct_img.rgb))
            frame = np.array(frame, dtype=np.uint8)
            results = self.model(frame)
            annotated_frame = results[0].plot()
            self.update_overlay_callback(annotated_frame)

    def doNothing(self):
        return
    
    def fakeScreenshot(self):
        screenshot = ImageGrab.grab()
        return screenshot

    def predict_on_screenshot(self):
        screenshots = self.take_screenshots()
        fake_screenshots = self.fakeScreenshot()
        # WHERE INFERENCE OCCURS

    def take_screenshots(self):
        try:
            num_shots = 1
            print("Capturing screenshots for board modeling...")
            screenshots = []
            for index in range(num_shots):
                time.sleep(0.5)  # Delay between screenshots
                screenshot = ImageGrab.grab()
                screenshots.append(screenshot)
                print(f"Captured screenshot #{index + 1}")
            return screenshots
        except Exception as e:
            print(f"Error in take_screenshots: {e}")
