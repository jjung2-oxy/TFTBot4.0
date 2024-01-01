# MainApp.py
import os
import platform
import sys
import threading

from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QApplication

import overlay
import threadedMain


def clear_terminal():
    if platform.system() == "Windows":
        os.system('cls')  # For Windows
    else:
        os.system('clear')  # For Linux/OS X

class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.overlay = overlay.Overlay(self.app)
        self.threaded_main = threadedMain.ThreadedMain(self.update_overlay)
        self.start_threaded_main()
        self.overlay.close_signal.connect(self.threaded_main.stop_listener)
        self.overlay.run_signal.connect(self.threaded_main.predict_on_screenshot)

    def update_overlay(self, frame):
        qImg = QImage(frame.data, frame.shape[1], frame.shape[0], frame.strides[0], QImage.Format_RGB888).rgbSwapped()
        self.overlay.set_annotated_frame(qImg)

    def start_threaded_main(self):
        self.thread = threading.Thread(target=self.threaded_main.run)
        self.thread.start()

    def run(self):
        self.overlay.run()
        self.thread.join()

if __name__ == "__main__":
    app = MainApp()
    app.run()
    clear_terminal()
