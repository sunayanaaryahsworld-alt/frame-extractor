from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import shutil
import os
import cv2

from app.video_utils import extract_frames
from app.frame_selector import select_best_frame

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload-video/")
async def upload_video(file: UploadFile = File(...)):
    video_path = f"{UPLOAD_DIR}/{file.filename}"

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    frames = extract_frames(video_path)
    best_frame = select_best_frame(frames)

    if best_frame is None:
        return {"error": "No suitable frame found"}

    output_path = f"{OUTPUT_DIR}/best_frame.jpg"
    cv2.imwrite(output_path, best_frame)

    return {"success": True}


@app.get("/result")
def get_result():
    return FileResponse("outputs/best_frame.jpg")


