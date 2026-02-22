from fastapi import FastAPI, File, UploadFile, Header, HTTPException
from fastapi.responses import FileResponse
import os
import shutil
import uuid
import subprocess
import imageio_ffmpeg

app = FastAPI()

API_KEY = "sahil_mp3_app_2026"

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.get("/")
def home():
    return {"status": "MP4 to MP3 API Running 🚀"}


# 🎬 CONVERT API
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
    mp3_filename = f"{unique_id}.mp3"
    mp3_path = os.path.join(OUTPUT_FOLDER, mp3_filename)

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

        command = [
            ffmpeg_path,
            "-i", video_path,
            "-vn",
            "-ab", "128k",
            "-ar", "44100",
            "-y",
            mp3_path
        ]

        subprocess.run(command, check=True)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 🔥 RETURN JSON INSTEAD OF FILE
    return {
        "status": "success",
        "download_url": f"/download/{mp3_filename}",
        "file_name": mp3_filename
    }


# ⬇ DOWNLOAD API
@app.get("/download/{file_name}")
def download_file(file_name: str):

    file_path = os.path.join(OUTPUT_FOLDER, file_name)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename=file_name
    )
