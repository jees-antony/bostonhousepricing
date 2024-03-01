from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from typing import List
from PIL import Image
from io import BytesIO
import detect   #detect.py

app = FastAPI()

# Allo request from all origins -CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.post("/detect")
async def detect_and_return_image(image_file: UploadFile = File(...)):
    """
    Handler of /detect POST endpoint
    Receives uploaded file with a name "image_file",
    passes it through YOLOv8 object detection
    network and returns an array of bounding boxes.
    :return: a JSON array of objects bounding
    boxes in format
    [[x1,y1,x2,y2,object_type,probability],..]
    """
    buf = await image_file.read()
    boxes, class_prob = detect.detect_objects_on_image(Image.open(BytesIO(buf)))
    print(f'class proba {class_prob}')
    annotated_image = detect.annotate_image(Image.open(BytesIO(buf)), boxes)
    return {
        "annotated_image": detect.image_to_base64(annotated_image),
        "class_prob": class_prob
    }
