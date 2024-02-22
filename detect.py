import io
import uvicorn
from fastapi import FastAPI, File, UploadFile
from PIL import Image, ImageDraw, ImageFont
import torch
import torchvision.transforms as transforms
from torchvision import models
from yolov7 import detect  # Adapt model import based on your actual model

# Load the pre-trained YOLOv7 model (or any other suitable model)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = detect.Detector(device=device)  # Replace with your model loading code

# Define the FastAPI app
app = FastAPI()

# Function to process the uploaded image and perform object detection
async def detect_objects(image_bytes: bytes, model_name: str = "yolov7"):
    """
    Processes an uploaded image and performs object detection.

    Args:
        image_bytes (bytes): The image data as bytes.
        model_name (str, optional): The name of the model to use (e.g., "yolov7"). Defaults to "yolov7".

    Returns:
        Image: The processed image with bounding boxes and labels, or None if an error occurs.
    """

    try:
        # Load the image
        image = Image.open(io.BytesIO(image_bytes))

        # Preprocess the image (adapt based on your model's requirements)
        transform = transforms.Compose([
            transforms.Resize((640, 640)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        image = transform(image).unsqueeze(0)

        # Perform object detection using the loaded model
        results = model(image)

        # Draw bounding boxes and labels on the image
        img_draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("arial.ttf", 12)
        for result in results:
            for box in result.pandas().xyxy:
                x_min, y_min, x_max, y_max, conf, cls = box.values
                img_draw.rectangle(((x_min, y_min), (x_max, y_max)), outline=(255, 0, 0), width=2)
                label = f"{cls} ({conf:.2f})"
                img_draw.text((x_min + 5, y_min + 5), label, font=font, fill=(255, 0, 0))

        # Return the processed image as bytes
        return image.convert("RGB").tobytes()

    except Exception as e:
        print(f"Error during object detection: {e}")
        return None

# Endpoint to handle image upload and object detection
@app.post("/detect")
async def handle_image_upload(image: UploadFile = File(...)):
    """
    Handles image upload and returns the processed image with bounding boxes and labels.

    Args:
        image (UploadFile): The uploaded image file.

    Returns:
        Image: The processed image or error message in JSON format.
    """

    try:
        # Read the image bytes
        image_bytes = await image.read()

        # Perform object detection
        processed_image = await detect_objects(image_bytes)

        if processed_image is None:
            return {"error": "Error processing image"}

        # Return the processed image in JPEG format
        return uvicorn.Response(processed_image, media_type="image/jpeg")

    except Exception as e:
        print(f"Error handling image upload: {e}")
        return {"error": "Internal server error"}

# Run the FastAPI server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
