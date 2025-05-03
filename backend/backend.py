from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
import httpx
import os
import io

app = FastAPI(title="AI Avatar Orchestrator")

# Database setup
SQLALCHEMY_DATABASE_URL = 'sqlite:///../shared/avatar-database.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User model for database
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String(255))

# Avatar model for database
class Avatar(Base):
    __tablename__ = "avatars"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    avatar_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(String, nullable=False)

# Voice model for database
class Voice(Base):
    __tablename__ = "voices"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    audio_id = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(String, nullable=False)

# AvatarCreated model for storing generated videos
class AvatarCreated(Base):
    __tablename__ = "avatars_created"
    user_id = Column(String, primary_key=True, index=True)
    video_name = Column(String, nullable=False)
    video = Column(Text, nullable=False)

# Create database tables
Base.metadata.create_all(bind=engine)

# Pydantic models for request validation
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class AvatarRequest(BaseModel):
    text: str
    user_id: str
    avatar_id: str
    audio_id: str

# Pydantic models for response
class AvatarResponse(BaseModel):
    id: str
    name: str
    created_at: str

class VoiceResponse(BaseModel):
    id: str
    name: str
    created_at: str

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Enable CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Register endpoint
@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = pwd_context.hash(user.password)
    new_user = User(name=user.name, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User registered successfully"}

# Login endpoint
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    return {"message": "Login successful", "email": db_user.email}

# Extract for avatar endpoint
@app.post('/extract-for-avatar/')
async def extract_for_avatar(
    video: UploadFile = File(...),
    user_id: str = Form(...),
    avatar_id: str = Form(...),
    audio_id: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        video_bytes = await video.read()

        # Save avatar and voice to database
        from datetime import datetime
        new_avatar = Avatar(
            user_id=user_id,
            avatar_id=avatar_id,
            name=avatar_id,
            created_at=datetime.utcnow().isoformat()
        )
        new_voice = Voice(
            user_id=user_id,
            audio_id=audio_id,
            name=audio_id,
            created_at=datetime.utcnow().isoformat()
        )
        db.add(new_avatar)
        db.add(new_voice)
        db.commit()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://127.0.0.1:8001/extract-audio-and-bestframe/",
                files={
                    "video_file": (video.filename, video_bytes, video.content_type)
                },
                data={
                    "user_id": user_id,
                    "avatar_id": avatar_id,
                    "audio_id": audio_id
                },
                timeout=60.0
            )

        response.raise_for_status()
        return response.json()

    except httpx.RequestError as e:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"Request failed: {str(e)}")
    except httpx.HTTPStatusError as e:
        db.rollback()
        raise HTTPException(status_code=e.response.status_code, detail=f"XTTS service error: {e.response.text}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")

# Generate avatar endpoint
@app.post("/generate-avatar/")
async def generate_avatar(
    text: str = Form(...),
    user_id: str = Form(...),
    avatar_id: str = Form(...),
    audio_id: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        async with httpx.AsyncClient() as client:
            xtts_clone_response = await client.post(
                "http://127.0.0.1:8001/synthesize-voice-frame/",
                json={
                    "user_id": user_id,
                    "avatar_id": avatar_id,
                    "audio_id": audio_id,
                    "text": text
                },
                timeout=180.0
            )
            xtts_clone_response.raise_for_status()
            clone_data = xtts_clone_response.json()
            if not clone_data.get("success", False):
                raise HTTPException(status_code=500, detail="Voice Synthesis Failed.")

        async with httpx.AsyncClient() as client:
            sadtalker_response = await client.post(
                "http://127.0.0.1:8002/create-avatar/",
                data={
                    "audio_id": audio_id,
                    "user_id": user_id,
                    "avatar_id": avatar_id
                },
                timeout=3600
            )
            sadtalker_response.raise_for_status()
            video_data = sadtalker_response.json()

            video_path = video_data["video_path"]
            video_name = f"{avatar_id}+{audio_id}"

            try:
                with open(video_path, "rb") as video_file:
                    video_blob = video_file.read()
            except FileNotFoundError:
                raise HTTPException(status_code=500, detail=f"Video file not found: {video_path}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error reading video file: {str(e)}")

            new_avatar = AvatarCreated(
                user_id=user_id,
                video_name=video_name,
                video=video_blob.hex()
            )

            try:
                db.add(new_avatar)
                db.commit()
                db.refresh(new_avatar)
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")

            response = FileResponse(
                path=video_path,
                media_type="video/mp4"
            )

            try:
                os.remove(video_path)
            except Exception as e:
                print(f"Warning: Could not delete video file {video_path}: {e}")

            return response

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Synthesis/Avatar generation service error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Avatar generation error: {str(e)}")

# Get avatars endpoint
@app.get("/avatars/{user_id}", response_model=list[AvatarResponse])
async def get_avatars(user_id: str, db: Session = Depends(get_db)):
    avatars = db.query(Avatar).filter(Avatar.user_id == user_id).all()
    return [{"id": avatar.avatar_id, "name": avatar.name, "created_at": avatar.created_at} for avatar in avatars]

# Get voices endpoint
@app.get("/voices/{user_id}", response_model=list[VoiceResponse])
async def get_voices(user_id: str, db: Session = Depends(get_db)):
    voices = db.query(Voice).filter(Voice.user_id == user_id).all()
    return [{"id": voice.audio_id, "name": voice.name, "created_at": voice.created_at} for voice in voices]

# Get avatar video endpoint
@app.get("/avatar/{user_id}")
async def get_avatar(user_id: str, db: Session = Depends(get_db)):
    avatar = db.query(AvatarCreated).filter(AvatarCreated.user_id == user_id).first()
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    video_data = bytes.fromhex(avatar.video)
    return StreamingResponse(
        io.BytesIO(video_data),
        media_type="video/mp4",
        headers={"Content-Disposition": f"attachment; filename={avatar.video_name}.mp4"}
    )