from ultralytics import YOLO
import torch
import os
import tempfile

# Initialize the YOLO model
model = YOLO(r"weights/DEPLOY.pt")

def process_image_and_predict(img):
    # Crop image
    crop_box = (560, 0, 2000, 720)  # (start_x, start_y, end_x, end_y)
    cropped_img = img.crop(crop_box)

    # Predict
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False, mode='w+b') as tmpfile:
        cropped_img.save(tmpfile, format='PNG')
        tmpfile_name = tmpfile.name

    try:
        result = model.predict(tmpfile_name, task='detect', mode='predict', verbose=False, conf=0.25, imgsz=800)
        os.remove(tmpfile_name)
        return result[0].names, result[0].boxes.cls, result[0].boxes.xyxy[0]
    except Exception as e:
        print(f"Error during prediction: {e}")
        return ([], [], [])

def get_champion_names(champ_list, unit_ids):
    if isinstance(unit_ids, torch.Tensor):
        unit_ids = unit_ids.tolist()

    return [champ_list[unit_id] for unit_id in unit_ids if unit_id in champ_list]

def process_screenshots(screenshots):
    champions = []
    for index, screenshot in enumerate(screenshots, start=1):
        try:
            champ_list, unit_ids, _ = process_image_and_predict(screenshot)
            if champ_list and unit_ids:
                champions.extend(get_champion_names(champ_list, unit_ids))
            print(f"Processed screenshot #{index}")
        except Exception as e:
            print(f"Error processing screenshot #{index}: {e}")

    return champions
