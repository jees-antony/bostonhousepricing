from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from typing import List
from PIL import Image
import numpy as np
from io import BytesIO
from pathlib import Path
from ultralytics import YOLO

app = FastAPI()

# Load YOLOv8 pretrained model
model = YOLO('best.pt')

print("running from new app")
def detect_objects(image):
    # Perform object detection
    results = model(image)

    # Check if results is empty
    if not results:
        return None

    # Render bounding boxes on the image
    rendered_images = [result.render()[0] for result in results]

    # Convert numpy arrays to PIL Images
    images_with_boxes = [Image.fromarray(image_with_boxes) for image_with_boxes in rendered_images]


    return images_with_boxes

@app.post("/detect")
async def detect_and_return_image(file: UploadFile = File(...)):
    
    # Read the uploaded image
    contents = await file.read()
    image = Image.open(BytesIO(contents))

    # Detect objects in the uploaded image
    image_with_boxes = detect_objects(image)

    # Save the image with bounding boxes
    output_image_path = "image_with_boxes.jpg"
    image_with_boxes.save(output_image_path)

    # Return the image with bounding boxes
    return FileResponse(output_image_path)
