import torch
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from transformers import DetrImageProcessor, DetrForObjectDetection, OwlViTProcessor, OwlViTForObjectDetection
from ultralytics import YOLO
import ollama  
import uvicorn
from fastapi import FastAPI

# Initialize FastAPI
app = FastAPI()

# Load YOLOv8
yolo_model = YOLO("yolov8l.pt")

# Load DETR
detr_processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
detr_model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")

# Load OWL-ViT
owlvit_processor = OwlViTProcessor.from_pretrained("google/owlvit-base-patch32")
owlvit_model = OwlViTForObjectDetection.from_pretrained("google/owlvit-base-patch32")

# Define Labels for OWL-ViT with refined queries
owlvit_labels = [
    ["computer mouse", "rodent mouse"],  
    ["bat", "baseball bat"],
    ["glasses", "drinking glass", "eyeglasses"]
]

DIY_PROJECTS = {
    ("Arduino", "Breadboard"): "Build a basic LED circuit with an Arduino and a breadboard.",
    ("Microscope", "Test tube"): "Create a home science experiment to observe microorganisms.",
    ("Paintbrush", "Canvas"): "Make a mixed-media painting with different brush techniques.",
    ("Soldering iron", "Circuit board"): "Solder a simple electronic project like a blinking LED system.",
    ("Oscilloscope", "Multimeter"): "Test and analyze an AC/DC circuit with an oscilloscope.",
    ("Beaker", "Chemicals"): "Perform a safe pH indicator experiment with household acids and bases."
}

detected_objects_memory = []  # Store detected objects globally

def detect_with_yolo(image_path):
    """Runs YOLOv8 on the image and returns detected objects with bounding boxes."""
    image = cv2.imread(image_path)
    results = yolo_model(image, conf=0.4)  

    detected_objects = []
    boxes = []

    for r in results:
        for box in r.boxes.data:
            x1, y1, x2, y2, conf, class_id = box.tolist()
            label = yolo_model.names[int(class_id)]

            detected_objects.append(label)
            boxes.append(((x1, y1, x2, y2), label, conf))

    return detected_objects, boxes

def detect_with_detr(image):
    """Runs DETR on the image and returns detected objects with bounding boxes."""
    inputs = detr_processor(images=image, return_tensors="pt")
    
    with torch.no_grad():
        outputs = detr_model(**inputs)

    target_sizes = torch.tensor([image.size[::-1]])
    results = detr_processor.post_process_object_detection(outputs, target_sizes=target_sizes)[0]

    detected_objects = []
    boxes = []

    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        if score > 0.6:
            label_text = detr_model.config.id2label[label.item()]
            detected_objects.append(label_text)
            boxes.append((box.tolist(), label_text, score.item()))

    return detected_objects, boxes

def detect_with_owlvit(image):
    """Runs OWL-ViT for zero-shot object detection based on refined labels."""
    inputs = owlvit_processor(text=owlvit_labels, images=image, return_tensors="pt")

    with torch.no_grad():
        outputs = owlvit_model(**inputs)

    scores = outputs["logits"].squeeze(0).sigmoid()
    predicted_boxes = outputs["pred_boxes"].squeeze(0)

    detected_objects = []
    boxes = []

    for label_idx in range(scores.shape[0]):
        for box_idx in range(scores.shape[1]):
            confidence = scores[label_idx, box_idx].item()
            if confidence > 0.4:
                detected_objects.append(owlvit_labels[label_idx][0])  # Pick correct term
                boxes.append((predicted_boxes[box_idx].tolist(), owlvit_labels[label_idx][0], confidence))

    return detected_objects, boxes

def generate_ai_suggestion(detected_objects):
    """Queries Ollama (Mistral) for an experiment recommendation."""
    if not detected_objects:
        return "No objects detected."

    prompt = f"Suggest a DIY experiment using these items: {', '.join(detected_objects)}. Keep it short and practical.Give in form of steps/checkpoints so that it aids in calculation of points for the user"
    
    try:
        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"]
    except Exception as e:
        return f"AI suggestion failed: {e}"

def merge_predictions(yolo_objects, detr_objects, owlvit_objects):
    """Combines predictions from YOLO, DETR, and OWL-ViT using confidence scores."""
    object_scores = {}

    for obj in yolo_objects + detr_objects + owlvit_objects:
        object_scores[obj] = object_scores.get(obj, 0) + 1  # Count occurrences

    # Retain only objects detected by at least 2 models
    final_objects = [obj for obj, count in object_scores.items() if count >= 2]
    return final_objects if final_objects else list(object_scores.keys())

def resolve_label_ambiguity(detected_objects):
    """Uses LLM to infer the correct meaning of objects based on context."""
    if not detected_objects:
        return detected_objects

    prompt = f"Given this list of detected objects: {', '.join(detected_objects)}, " \
             f"correct any ambiguities (e.g., 'mouse' should be 'computer mouse' if a laptop is present). " \
             f"Return only the corrected list."

    try:
        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
        corrected_objects = response["message"]["content"].split(", ")
        return corrected_objects
    except Exception as e:
        print("Error resolving label ambiguity:", e)
        return detected_objects  # Fallback

@app.get("/")
def home():
    return {"message": "API is running! Use /detect or /chat endpoints."}

@app.get("/chat")
def chat(user_query: str):
    """Chatbot that helps with understanding detected objects."""
    if not detected_objects_memory:
        return {"response": "No objects detected yet. Run /detect first."}

    prompt = f"The detected objects are: {', '.join(detected_objects_memory)}. {user_query}"
    
    try:
        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
        return {"response": response["message"]["content"]}
    except Exception as e:
        return {"error": str(e)}
    
@app.get("/detect")
def detect_objects(image_path: str):
    """Detect objects in an image and return results with  JSON formatting."""
    global detected_objects_memory

    try:
        image = Image.open(image_path)

        yolo_objects, _ = detect_with_yolo(image_path)
        detr_objects, _ = detect_with_detr(image)
        owlvit_objects, _ = detect_with_owlvit(image)

        all_objects = merge_predictions(yolo_objects, detr_objects, owlvit_objects)
        corrected_objects = resolve_label_ambiguity(all_objects)

        detected_objects_memory = corrected_objects  # Store corrected objects

        diy_project = next((DIY_PROJECTS[key] for key in DIY_PROJECTS if all(item in corrected_objects for item in key)), None)

        if not diy_project:
            diy_project = generate_ai_suggestion(corrected_objects)  
        
        return {
            "detected_objects": corrected_objects,
            "diy_project": diy_project
        }
    
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print("Server Starting... Visit: http://0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
