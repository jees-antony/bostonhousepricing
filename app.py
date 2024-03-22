from fastapi import FastAPI, File, UploadFile, Request, HTTPException, Depends
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordBearer
from typing import List
from PIL import Image
import json
from io import BytesIO
import uuid
import os
from database import database
from pydantic import BaseModel
import jwt

import detect   #detect.py
import auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    #On Startup
    await database.connect()
    yield
    #On Shutdown
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="templates")

# Secret key to sign JWT token
SECRET_KEY = "mysecretkey"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

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
    preds = await database.fetch_one(f"SELECT preds, image_file FROM pred_tb WHERE id = {prediction_id};")
    print(preds.image_file)
    image_file = preds.image_file
    image_path = str(image_file) + ".png"
    image_path = os.path.join("images", image_path)

    pred_dic = json.loads(preds.preds)
    treat_dic = {}
    for p in pred_dic:
        print(p)
        treat = await database.fetch_one(f"SELECT treat FROM treatments_tb WHERE name = '{p}';")
        treat_dic[p] = treat.treat
    if treat_dic:
        # print(json.loads(treat_dic))
        # print(treat_dic)
        # treat_dic = treat_dic.replace("\\", "")
        treat_dic = json.dumps(treat_dic)
        return {
            "treatments": json.loads(treat_dic),
            "image": detect.imagefile_to_base64(image_path)
        }
    else:
        raise HTTPException(status_code=404, detail="Treatment details not found")
# Function to verify JWT token
def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.get("/")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/detect")
async def detect_page(request: Request):
    return templates.TemplateResponse("detect_page.html", {"request": request})

@app.post("/detect_api")
async def detect_and_return_image(image_file: UploadFile = File(...), token: str = Depends(verify_token)):
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

    # inser image file name and predictions id into DB
    username = token
    query = f'''
                WITH user_info AS (
                SELECT id AS user_id
                FROM users
                WHERE username = '{username}'
            ), inserted_rows AS (
                INSERT INTO preds_tb (pred_user_id)
                SELECT user_id FROM user_info
                RETURNING id
            ), predicted_image_insert AS (
                INSERT INTO pred_images (pred_id, pred_img_file)
                SELECT id, '{image_uuid}' FROM inserted_rows
            )
            SELECT id FROM inserted_rows;'''
    #return pred-id for current predition
    pred_id = await database.execute(query=query)

    #inserting disease and proba into db
    prob_json = {}
    for prob in class_prob:
        prob_json[prob[0]] = prob[1]

    treat_dic = {}
    for disea, prob in prob_json.items():
        print(disea)
        disea_rec = await database.fetch_one(f"SELECT id, treat FROM disease_tb WHERE disease = '{disea}';")
        print(f"disease rec: {disea_rec}")

        if disea_rec:
            disea_id, treat = disea_rec.id, disea_rec.treat
            print(f"disease id: {disea_id}, treat : {treat[:50]}")
        else:
            continue

        treat_dic[disea] = treat

        await database.execute(
        f"INSERT INTO pred_diseases (pred_id, disease_id, proba) VALUES ({pred_id}, '{disea_id}', {prob});"
    )
        
    if treat_dic:
        treat_dic = json.dumps(treat_dic)
        treat_dic = json.loads(treat_dic)

    prob_json = json.dumps(prob_json)

    print(pred_id)
    return {
        "annotated_image": detect.image_to_base64(annotated_image),
        "class_prob": class_prob,
        "treatments": treat_dic
    }

#for getting the predicted images list
@app.get("/predicted/")
async def detect_and_return_image(request: Request):
    return templates.TemplateResponse("predictions.html", {"request": request})

@app.get("/api/predicted/")
async def api_predicted(token: str = Depends(verify_token), response_model=list[Prediction]):
    return await fetch_predictions()

@app.get("/treatments/{pred_id}")
async def get_treatment(pred_id:int, token: str = Depends(verify_token)):
    return await fetch_treatment_details(pred_id)


# Example endpoint for user registration
@app.post("/register")
async def register(username: str, password: str):
    # Check if the username already exists in the database
    existing_user = await database.fetch_one(f"SELECT username FROM users WHERE username = '{username}'")
    print(existing_user)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Save the new user to the database
    await auth.save_user(username, password)
    return {"message": "User registered successfully"}

class LoginCredentials(BaseModel):
    username: str
    password: str

# token creation on login
@app.post("/token")
async def login(credentials: LoginCredentials):
    username = credentials.username
    password = credentials.password

    if not await auth.authenticate_user(username, password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = auth.create_jwt_token(username)
    return {"access_token": token, "token_type": "bearer"}

# to get username who is logged in with token
# @app.get("/users/me")
# async def read_users_me(token: str = Depends(oauth2_scheme)):
async def read_users_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {username}

# @app.get("/users/get")
# async def read_users_me(token: str = Depends(verify_token)):
#     return "you are authorised"