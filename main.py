
from PyQt5.QtWidgets import QApplication
import overlay
import sys

class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)  # Create the QApplication instance first
        self.overlay = overlay.Overlay(self.app)

    def run(self):
        self.overlay.run()


if __name__ == "__main__":
    print("\n\nRunning MAIN\n\n")
    app = MainApp()
    app.run()