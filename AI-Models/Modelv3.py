import torch
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from transformers import DetrImageProcessor, DetrForObjectDetection, OwlViTProcessor, OwlViTForObjectDetection
from ultralytics import YOLO
import ollama  # Local AI for project recommendations

# Load YOLOv8
yolo_model = YOLO("yolov8l.pt")

# Load DETR
detr_processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
detr_model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")

# Load OWL-ViT
owlvit_processor = OwlViTProcessor.from_pretrained("google/owlvit-base-patch32")
owlvit_model = OwlViTForObjectDetection.from_pretrained("google/owlvit-base-patch32")

owlvit_labels = ["Arduino", "Breadboard", "Multimeter", "Soldering iron", "Oscilloscope", 
                 "Microscope", "Test tube", "Beaker", "Paintbrush", "Canvas", "Pencil"]

DIY_PROJECTS = {
    ("Arduino", "Breadboard"): "💡 Build a basic LED circuit with an Arduino and a breadboard.",
    ("Microscope", "Test tube"): "🔬 Create a home science experiment to observe microorganisms.",
    ("Paintbrush", "Canvas"): "🎨 Make a mixed-media painting with different brush techniques.",
    ("Soldering iron", "Circuit board"): "🛠 Solder a simple electronic project like a blinking LED system.",
    ("Oscilloscope", "Multimeter"): "⚡ Test and analyze an AC/DC circuit with an oscilloscope.",
    ("Beaker", "Chemicals"): "🧪 Perform a safe pH indicator experiment with household acids and bases."
}

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
    """Runs OWL-ViT for zero-shot object detection based on defined labels."""
    inputs = owlvit_processor(text=[[label] for label in owlvit_labels], images=image, return_tensors="pt")

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
                detected_objects.append(owlvit_labels[label_idx])
                boxes.append((predicted_boxes[box_idx].tolist(), owlvit_labels[label_idx], confidence))

    return detected_objects, boxes



def recommend_diy_project(detected_objects):
    """Matches detected objects with predefined DIY projects."""
    for key in DIY_PROJECTS:
        if all(item in detected_objects for item in key):
            return DIY_PROJECTS[key]
    
    return None

def generate_ai_suggestion(detected_objects):
    """Queries a local AI model (Ollama) for experiment recommendations."""
    if not detected_objects:
        return "No objects detected."

    prompt = f"Suggest a DIY experiment using these items: {', '.join(detected_objects)}. Keep it short and practical."
    
    try:
        response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"]
    except Exception as e:
        return "Try building a creative structure using the detected objects!"

def draw_boxes(image, boxes):
    """Draws bounding boxes on the image."""
    fig, ax = plt.subplots(1, figsize=(10, 6))
    ax.imshow(image)

    for box, label, score in boxes:
        if len(box) == 4:
            x1, y1, x2, y2 = box
        else:
            x, y, w, h = box
            x1, y1, x2, y2 = x, y, x + w, y + h

        rect = patches.Rectangle((x1, y1), x2 - x1, y2 - y1, linewidth=2, edgecolor="r", facecolor="none")
        ax.add_patch(rect)
        ax.text(x1, y1, f"{label} ({score:.2f})", fontsize=10, color="white",
                bbox=dict(facecolor="red", alpha=0.5))

    plt.axis("off")
    plt.show()

# Load image
image_path = "table.jpeg"  
image = Image.open(image_path)

# Run YOLOv8, DETR, and OWL-ViT
yolo_objects, yolo_boxes = detect_with_yolo(image_path)
detr_objects, detr_boxes = detect_with_detr(image)
owlvit_objects, owlvit_boxes = detect_with_owlvit(image)

all_objects = list(set(yolo_objects + detr_objects + owlvit_objects))
all_boxes = yolo_boxes + detr_boxes + owlvit_boxes

# Show detected objects
print("\n Detected Objects:", all_objects)

# Generate DIY recommendation
diy_project = recommend_diy_project(all_objects)
if diy_project:
    print("\n🛠DIY Project Recommendation:", diy_project)
else:
    ai_suggestion = generate_ai_suggestion(all_objects)
    print("\n Suggested DIY Project:", ai_suggestion)

# Show image with bounding boxes
draw_boxes(image, all_boxes)
