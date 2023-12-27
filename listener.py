# listener.py
from pynput.keyboard import Key, Listener

class KeyboardListener:
    def __init__(self, on_esc_press_callback):
        self.listener = None
        self.on_esc_press_callback = on_esc_press_callback

    def start_listener(self):
        with Listener(on_press=self.on_press) as self.listener:
            self.listener.join()

    def stop_listener(self):
        if self.listener:
            self.listener.stop()

    def on_press(self, key):
        try:
            if key == Key.esc:
                self.on_esc_press_callback()  # Call the callback when ESC is pressed
        except Exception as e:
            print(f"Error in on_press: {e}")
