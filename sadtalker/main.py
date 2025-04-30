from fastapi import HTTPException, FastAPI, Form
from pydantic import BaseModel
from sadtalker_utils import run_sadtalker
import os

app = FastAPI(title="SadTalker API")

class VideoResponse(BaseModel):
    user_id: str
    avatar_id: str
    video_path: str

@app.post("/create-avatar/", response_model=VideoResponse)
async def create_avatar_endpoint(
    audio_file: str = Form(...),
    best_image: str = Form(...),
    user_id: str = Form(...),
    avatar_id: str= Form(...)
):
    try:
        if not audio_file.lower().endswith('.wav'):
            raise HTTPException(status_code=400, detail="Invalid audio format. Only .wav is supported.")
        if not best_image.lower().endswith(('.jpg', '.png')):
            raise HTTPException(status_code=400, detail="Invalid image format. Only .jpg or .png is supported.")

        video_path = f"avatar_generated/{user_id}_{avatar_id}_avatar.mp4"
        os.makedirs(video_path, exist_ok=True)

        run_sadtalker(
            cloned_audio_output=audio_file,
            input_image=best_image,
            result_dir=video_path
        )

        return VideoResponse(user_id=user_id, avatar_id=avatar_id, video_path=video_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Creating Avatar: {str(e)}")
