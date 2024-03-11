from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from typing import List
from PIL import Image
import json
from io import BytesIO
import detect   #detect.py
import uuid
import os
from databases import Database
from pydantic import BaseModel

database = Database("sqlite:///cocoa-ml.db")
@asynccontextmanager
async def lifespan(app: FastAPI):
    #On Startup
    await database.connect()
    yield
    #On Shutdown
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

class Prediction(BaseModel):
    id: int
    predictions: str

# Allo request from all origins -CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

async def fetch_predictions() -> list[Prediction]:
    query = 'SELECT id, preds FROM pred_tb'
    predictions = await database.fetch_all(query)
    pred_itm = [Prediction(id=row[0], predictions=row[1]) for row in predictions]
    print(pred_itm)
    return pred_itm

async def fetch_treatment_details(prediction_id: int):
    preds = await database.fetch_one(f"SELECT preds FROM pred_tb WHERE id = {prediction_id};")
    print(preds.preds)
    pred_dic = json.loads(preds.preds)
    treat_dic = {}
    for p in pred_dic:
        print(p)
        treat = await database.fetch_one(f"SELECT treat FROM treatments_tb WHERE name = '{p}';")
        treat_dic[p] = treat.treat
    if treat_dic:
        return json.dumps(treat_dic)
    else:
        raise HTTPException(status_code=404, detail="Treatment details not found")

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

    image_uuid = uuid.uuid4()
    image_path = str(image_uuid) + ".png"
    image_path = os.path.join("images", image_path)
    # save image as PNG
    annotated_image.save(image_path)

    # inser image file name and predictions into DB
    prob_json = {}
    for prob in class_prob:
        prob_json[prob[0]] = prob[1]
    prob_json = json.dumps(prob_json)
    query = f"INSERT INTO pred_tb (image_file, preds) VALUES ('{str(image_uuid)}','{prob_json}');"
    await database.execute(query=query)

    return {
        "annotated_image": detect.image_to_base64(annotated_image),
        "class_prob": class_prob,
        "treatments": "treatments"
    }

#for getting the predicted images list
@app.get("/predicted/")
async def detect_and_return_image(request: Request):
    return templates.TemplateResponse("predictions.html", {"request": request})

@app.get("/api/predicted/")
async def api_predicted(response_model=list[Prediction]):
    return await fetch_predictions()

@app.get("/treatments/{pred_id}")
async def get_treatment(pred_id:int):
    return await fetch_treatment_details(pred_id)