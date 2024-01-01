import cv2
import numpy as np
from mss import mss
from PIL import Image
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO('weights/DEPLOY.pt')  # Replace 'yolov8n.pt' with your model path if different

# Set up screen capture
sct = mss()
monitor = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}  # Adjust the size as needed

while True:
    # Capture the screen
    sct_img = sct.grab(monitor)
    frame = np.array(Image.frombytes('RGB', (sct_img.width, sct_img.height), sct_img.rgb))

    # Convert the image from RGB to BGR format (as required by OpenCV)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    # Run YOLOv8 inference on the frame
    results = model(frame)

    # Visualize the results on the frame
    annotated_frame = results[0].plot()  # Ensure that this is the correct way to visualize in your version of YOLO

    # Display the annotated frame
    cv2.imshow("YOLOv8 Inference", annotated_frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Close the display window
cv2.destroyAllWindows()
