from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Query
from model_config import load_model
from utils import extract_audio, clone_audio, save_to_db
from typing import Optional, Union
from pydantic import BaseModel
import os 
from best_frame_extractor import extract_best_avatar_frame 

app = FastAPI(title="Voice Cloning API")

class AudioResponse(BaseModel):
    user_id: str
    audio_path : Optional[str] = None
    message: str

class VoiceCloneRequest(BaseModel):
    user_id : str
    text: str
    reference_audio_path: str

class CombinedResponse(BaseModel):
    user_id: str
    audio_path : Optional[str] = None
    frame_path: Optional[str] = None
    message: str

model = load_model()
model.cpu()

@app.post("/extract-audio-bestframe/", response_model=CombinedResponse)
async def extract_audio_endpoint(video_file: UploadFile = File(...), user_id: str = Form(...)):
    #Extract audio from uploaded video file
    try:
        if not video_file.filename.lower().endswith(('.mp4','.mov','.avi')):
            raise HTTPException(status_code=400, detail="Invalid File Format.")
        
        video_path = f"uploaded_videos/{user_id}_{video_file.filename}"
        os.makedirs("uploaded_videos", exist_ok=True)
        with open(video_path,'wb') as f:
            f.write(await video_file.read())

        audio_path = f"extracted_audios/{user_id}_extracted.wav"
        os.makedirs("extracted_audios", exist_ok=True)

        extract_audio(video_path,audio_path)
        save_to_db(user_id, audio_path)

        frame_path = extract_best_avatar_frame(video_path, output_dir="best_frames", user_id=user_id)

        return CombinedResponse(
            user_id=user_id,
            audio_path=audio_path,
            frame_path=frame_path,
            message="Audio Extracted Successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    

@app.post('/clone-voice/', response_model=AudioResponse)
async def clone_voice_endpoint(request: VoiceCloneRequest):
    try:
        if not request.text:
            raise HTTPException(status_code=400, detail='Text input is required!')
        
        output_audio_path = f"generated_audios/{request.user_id}_generated.wav"
        os.makedirs("generated_audios", exist_ok=True)
        clone_audio(model, request.user_id, request.text, output_audio_path)
        return AudioResponse(
            user_id=request.user_id,
            audio_path=output_audio_path,
            message="Voice Cloned Successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error Cloning Voice: {str(e)}")

@app.get("/generated-audio/", response_model=AudioResponse)
async def display_generated_audio(user_id: str = Query(...)):
    try:
        output_audio_path = f"generated_audios/{user_id}_generated.wav"

        if not os.path.exists(output_audio_path):
            raise HTTPException(status_code=404, detail="Audio file not found.")
        
        return AudioResponse(
            user_id= user_id,
            audio_path=output_audio_path,
            message="Displayed Generated Voice Successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Displaying Generated Audio: {str(e)}")

@app.get("/extracted-audio/", response_model=AudioResponse)
async def display_extracted_audio(user_id: str=Query(...)):
    try:
        audio_path = f"extracted_audios/{user_id}_extracted.wav"
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail="Audio Not Found.")
        
        return AudioResponse(
            user_id=user_id,
            audio_path=audio_path,
            message="Displayed Extracted Voice Successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error displaying extracted audio.")
    
    
