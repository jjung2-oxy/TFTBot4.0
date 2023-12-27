# threadedMain.py
from listener import KeyboardListener
from PIL import ImageGrab
import threading
import time

class ThreadedMain:
    def __init__(self):
        self.keyboard_listener = KeyboardListener(self.doNothing)

    def run(self):
        listener_thread = threading.Thread(target=self.keyboard_listener.start_listener)
        listener_thread.start()

    def stop_listener(self):
        self.keyboard_listener.stop_listener()

    def predict_on_screenshot(self):
        screenshots = self.take8_screenshots()
        # ... add logic to process screenshots ...
    
    def doNothing(self):
        return

    def take8_screenshots(self):
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
