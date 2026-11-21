import cv2
from ultralytics import YOLO

# Load YOLO model
model = YOLO("yolo11n.pt")


def detect_video(video_path):

    cap = cv2.VideoCapture(video_path)

    detected_objects = set()

    if not cap.isOpened():
        return ["Unable to open video"]

    frame_count = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        # Analyse every 30th frame
        if frame_count % 30 == 0:

            results = model(frame)

            for result in results:
                for box in result.boxes:

                    class_id = int(box.cls[0])
                    object_name = model.names[class_id]

                    detected_objects.add(object_name)

        frame_count += 1

    cap.release()

    return list(detected_objects)