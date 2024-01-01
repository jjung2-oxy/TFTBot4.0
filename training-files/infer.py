from ultralytics import YOLO

# Define a glob search for all JPG files in a directory

model = YOLO('weights//DEPLOY.pt')

source = '/Users/jordanjung/Library/Mobile Documents/com~apple~CloudDocs/CODE/TFTBot4.0/training-files/images/'
project = 'training-files/processed'

# Run inference on the source
model.predict(source, save=True, imgsz=800, conf=0.7, project=project)                                 
    