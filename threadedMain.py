import threading
import time

from PIL import ImageGrab

import inference
from listener import KeyboardListener


class ThreadedMain:
    def __init__(self):
        self.keyboard_listener = KeyboardListener(self.doNothing)

    def run(self):
        listener_thread = threading.Thread(target=self.keyboard_listener.start_listener)
        listener_thread.start()

    def stop_listener(self):
        self.keyboard_listener.stop_listener()


    # PRIMARY MAIN FUNCTIONS

    def doNothing(self):
        return
    
    def fakeScreenshot(self):
        screenshot = ImageGrab.grab()
        return screenshot

    def predict_on_screenshot(self):
        screenshots = self.take_screenshots()
        fake_screenshots = self.fakeScreenshot()
        
        champions = inference.process_screenshots(fake_screenshots)
    
    def take_screenshots(self):
        try:
            
            # NUMBER OF SCREENSHOTS TO TAKE
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
            print(f"Error in take8_screenshots: {e}")
