from fastapi import FastAPI, File, UploadFile, Header, HTTPException
from fastapi.responses import FileResponse
import os
import shutil
from moviepy.editor import VideoFileClip
import uuid

app = FastAPI()

API_KEY = "sahil_mp3_app_2026"

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.get("/")
def home():
    return {"message": "MP4 to MP3 API is running 🚀"}


@app.post("/convert")
async def convert_video(
    file: UploadFile = File(...),
    x_api_key: str = Header(None)
):

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    if not file.filename.endswith(".mp4"):
        raise HTTPException(status_code=400, detail="Only MP4 files allowed")

    unique_id = str(uuid.uuid4())
    video_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}.mp4")

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        video = VideoFileClip(video_path)

        original_name = os.path.splitext(file.filename)[0]
        clean_name = original_name.replace(" ", "_")

        mp3_filename = f"{clean_name}.mp3"
        mp3_path = os.path.join(OUTPUT_FOLDER, mp3_filename)

        video.audio.write_audiofile(mp3_path)
        video.close()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FileResponse(
        mp3_path,
        media_type="audio/mpeg",
        filename=mp3_filename
    )
