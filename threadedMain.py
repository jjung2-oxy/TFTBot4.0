from pynput.keyboard import Key, Listener
import threading

class ThreadedMain:
    def __init__(self):
        self.listener = None

    def run(self):
        listener_thread = threading.Thread(target=self.start_listener)
        listener_thread.start()
        listener_thread.join()  

    def start_listener(self):
        with Listener(on_press=self.on_press) as self.listener:
            self.listener.join()  
    
    def stop_listener(self):
        if self.listener:
            self.listener.stop()

    def on_press(self, key):
        try:
            if key == Key.esc:
                print("ESC pressed... Stopping listener thread")
                self.listener.stop()
        except Exception as e:
            print(f"Error in on_press: {e}")

if __name__ == "__main__":
    threaded_main = ThreadedMain()
    threaded_main.run()
