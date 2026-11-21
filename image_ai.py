from ultralytics import YOLO

# Load YOLO object detection model
model = YOLO("yolo11n.pt")


def detect_objects(image_path):
    results = model(image_path)

    detected_objects = []

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            object_name = model.names[class_id]
            detected_objects.append(object_name)

    return detected_objects