import cv2
import numpy as np
import torch
import ollama  
from ultralytics import YOLO

model = YOLO("yolov8l.pt")  # Large model for better accuracy

# Memory buffer for detected objects
seen_objects = {}

def detect_objects(frame):
    """Runs YOLOv8 on the frame and returns detected objects with bounding boxes."""
    results = model(frame, conf=0.4)  

    detected_items = []

    for r in results:
        for box in r.boxes.data:
            x1, y1, x2, y2, conf, class_id = box.tolist()
            label = model.names[int(class_id)]

            if label not in seen_objects:
                seen_objects[label] = {"count": 1, "bbox": (int(x1), int(y1), int(x2), int(y2))}
            else:
                seen_objects[label]["count"] += 1

            detected_items.append(label)

            # Draw bounding box
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(frame, f"{label} ({conf:.2f})", (int(x1), int(y1)-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return detected_items, frame

def query_local_llm(objects):
    """Sends detected objects to Ollama for experiment recommendations."""
    if not objects:
        return "No objects detected."

    prompt = f"Suggest a DIY experiment using these items: {', '.join(objects)}. Give a short but clear project idea."

    try:
        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"]
    except Exception as e:
        print(f"Ollama error: {e}")
        return "Try building a creative structure using the detected objects!"

frame_path = "/home/anjana/Desktop/SNUHacks/table.jpeg" 
frame = cv2.imread(frame_path)

if frame is None:
    print("Error: Could not read the image file.")
else:
    # Detect objects in the frame
    detected_objects, processed_frame = detect_objects(frame)

    cv2.imshow("Object Detection", processed_frame)
    cv2.waitKey(2000)  
    cv2.destroyAllWindows()

    # Query AI model only if new objects are found
    if detected_objects:
        print("\nDetected Objects:", detected_objects)
        recommendation = query_local_llm(detected_objects)
        print("\nDIY Experiment Recommendation:", recommendation)
