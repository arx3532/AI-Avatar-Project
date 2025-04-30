from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import httpx
import os
import uuid
from typing import Optional

app = FastAPI(title="AI Avatar Orchestrator")

class AvatarRequest(BaseModel):
    text: str
    user_id: str
    avatar_id: str

@app.post("/generate-avatar/")
async def generate_avatar(
    video: UploadFile = File(...),
    text: str = Form(...),
    user_id: str = Form(...),
    avatar_id: str = Form(...)
):
    """End-to-end avatar generation pipeline with avatar_id tracking"""
    try:
        # Generate unique session ID for tracing
        session_id = str(uuid.uuid4())

        # Step 1: Extract audio and best frame using XTTS
        async with httpx.AsyncClient() as client:
            # Upload video to XTTS with avatar_id
            xtts_extract_response = await client.post(
                "http://xtts:8001/extract-audio-and-bestframe/",
                files={"video_file": (video.filename, await video.read(), video.content_type)},
                data={"user_id": user_id, "avatar_id": avatar_id}
            )
            xtts_extract_response.raise_for_status()
            extraction_data = xtts_extract_response.json()

        # Step 2: Clone voice using extracted audio with avatar_id
        async with httpx.AsyncClient() as client:
            xtts_clone_response = await client.post(
                "http://xtts:8001/clone-voice/",
                json={
                    "user_id": user_id,
                    "avatar_id": avatar_id,
                    "text": text,
                    "reference_audio_path": extraction_data["audio_path"]
                }
            )
            xtts_clone_response.raise_for_status()
            clone_data = xtts_clone_response.json()

        # Step 3: Generate avatar video using SadTalker with avatar_id
        async with httpx.AsyncClient() as client:
            sadtalker_response = await client.post(
                "http://sadtalker:8002/create-avatar/",
                data={
                    "audio_file": clone_data["audio_path"],
                    "best_image": extraction_data["frame_path"],
                    "user_id": user_id,
                    "avatar_id": avatar_id
                }
            )
            sadtalker_response.raise_for_status()
            video_data = sadtalker_response.json()

        # Step 4: Return generated video with metadata
        return {
            "avatar_id": avatar_id,
            "user_id": user_id,
            "video_url": f"/avatars/{user_id}/{avatar_id}/result.mp4",
            "download": FileResponse(
                path=os.path.join(video_data["video_path"], "result.mp4"),
                media_type="video/mp4",
                filename=f"{user_id}_{avatar_id}_avatar.mp4"
            )
        }

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Service error: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Orchestration error: {str(e)}"
        )



