# yolov8_processing.py
import cv2
import numpy as np
from mss import mss
from PIL import Image
from PyQt5.QtCore import QObject, pyqtSignal
from ultralytics import YOLO


class FrameProcessor(QObject):
    new_frame = pyqtSignal(np.ndarray)

    def __init__(self, model_path):
        super().__init__()
        self.model = YOLO(model_path)

    def process_frame(self, frame):
        results = self.model(frame)
        annotated_frame = results[0].plot()
        self.new_frame.emit(annotated_frame)

def capture_screen(processor):
    sct = mss()
    monitor = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}

    while True:
        sct_img = sct.grab(monitor)
        frame = np.array(Image.frombytes('RGB', (sct_img.width, sct_img.height), sct_img.rgb))
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        processor.process_frame(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    processor = FrameProcessor('weights/DEPLOY.pt')
    capture_screen(processor)
