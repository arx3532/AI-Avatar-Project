from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Query
from model_config import load_model
from utils import extract_audio, clone_output, save_to_db, load_audio
from typing import Optional
from pydantic import BaseModel
import os 
from best_frame_extractor import extract_best_avatar_frame, load_image_from_db
import cv2
import shutil

app = FastAPI(title="Voice Cloning API")

class AudioResponse(BaseModel):
    user_id: str
    audio_id: str
    audio_path : Optional[str] = None
    message: Optional[str] = None

class GeneratorRequest(BaseModel):
    user_id : str
    avatar_id: str
    audio_id: str
    text: str

class DisplayRequest(BaseModel):
    user_id: str
    avatar_id: str
    audio_id: str

class CombinedResponse(BaseModel):
    user_id: str
    avatar_id: str
    audio_id: str
    success: bool


model = load_model()
model.cpu()

@app.post("/extract-audio-and-bestframe/", response_model=CombinedResponse)
async def extract_audio_frame_endpoint(video_file: UploadFile = File(...), user_id: str = Form(...), avatar_id: str = Form(...), audio_id: str = Form(...)):
    #Extract audio from uploaded video file
    print("RUNNING@!!!")
    try:
        if not video_file.filename.lower().endswith(('.mp4','.mov','.avi')):
            raise HTTPException(status_code=400, detail="Invalid File Format.")
        
        video_path = f"../shared/uploaded_videos/{user_id}_{avatar_id}_{audio_id}_{video_file.filename}"
        os.makedirs("../shared/uploaded_videos", exist_ok=True)
        with open(video_path,'wb') as f:
            f.write(await video_file.read())

        audio_path = f"../shared/extracted_audios/{user_id}_{audio_id}_extracted.wav"
        os.makedirs("../shared/extracted_audios", exist_ok=True)

        extract_audio(video_path,audio_path)
        save_to_db(user_id, audio_id,  audio_path)

        extract_best_avatar_frame(
            video_path=video_path,
            user_id=user_id,
            avatar_id=avatar_id
        )
        try:
            clear_folder("../shared/uploaded_videos")
            clear_folder("../shared/extracted_audios")
        except Exception as cleanup_err:
            print(f"Cleanup failed: {cleanup_err}")

        return CombinedResponse(
            user_id=user_id,
            audio_id=audio_id,
            avatar_id=avatar_id,
            success= True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    

@app.post('/synthesize-voice-frame/', response_model=CombinedResponse)
async def synthesize_endpoint(request: GeneratorRequest):
    print("keri")
    try:
        print(request.user_id)
        print("keri2")
        if not request.text:
            raise HTTPException(status_code=400, detail='Text input is required!')
        
        output_audio_path = f"../shared/generated_audios/{request.user_id}_{request.audio_id}_generated.wav"
        os.makedirs("../shared/generated_audios", exist_ok=True)
        temp_audio_path = load_audio(request.user_id, request.audio_id)
        clone_output(model, request.text, output_audio_path, temp_audio_path)
        
        print("kazhinju")
        print(f"user_id={request.user_id}")
        
        return CombinedResponse(
            user_id=request.user_id,
            avatar_id = request.avatar_id,
            audio_id = request.audio_id,
            success= True
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@app.get("/generated-audio/", response_model=AudioResponse)
async def display_generated_audio(request: DisplayRequest):
    try:
        output_audio_path = load_audio(request.user_id, request.audio_id)
        if not os.path.exists(output_audio_path):
            raise HTTPException(status_code=404, detail="Audio file not found.")
        
        return AudioResponse(
            user_id= request.user_id,
            audio_id = request.audio_id,
            audio_path=output_audio_path,
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Displaying Generated Audio: {str(e)}")

@app.get("/extracted-audio/", response_model=AudioResponse)
async def display_extracted_audio(user_id: str=Query(...), audio_id: str = Query(...)):
    try:
        audio_path = f"../shared/extracted_audios/{user_id}_{audio_id}_extracted.wav"
        if not os.path.exists(audio_path):
            raise HTTPException(status_code=404, detail="Audio Not Found.")
        
        return AudioResponse(
            user_id=user_id,
            audio_id = audio_id,
            audio_path=audio_path
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error displaying extracted audio.")
    
    

def clear_folder(folder_path: str):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")