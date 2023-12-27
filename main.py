import sys
from PyQt5.QtWidgets import QApplication
import overlay
import threading
import threadedMain 

class MainApp:
    def __init__(self):
        # OVERLAY INIT
        self.app = QApplication(sys.argv)  
        self.overlay = overlay.Overlay(self.app)

        #  THREADED MAIN INIT
        self.threaded_main = threadedMain.ThreadedMain()
        self.start_threaded_main()

        # SIGNAL INIT
        self.overlay.close_signal.connect(self.threaded_main.stop_listener)
        self.overlay.run_signal.connect(self.threaded_main.predict_on_screenshot)

    def start_threaded_main(self):
        self.thread = threading.Thread(target=self.run_threaded_main)
        self.thread.start()

    def run_threaded_main(self):
        self.threaded_main.run()

    def run(self):
        self.overlay.run()

if __name__ == "__main__":
    app = MainApp()
    app.run() 
    app.thread.join()
