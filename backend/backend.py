from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import httpx
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext

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

# Create database tables
Base.metadata.create_all(bind=engine)

class AvatarRequest(BaseModel):
    text: str
    user_id: str
    avatar_id: str
    audio_id: str

# Pydantic models for request validation
class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FastAPI app
app = FastAPI()

# Enable CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
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
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password
    hashed_password = pwd_context.hash(user.password)
    
    # Create and save new user
    new_user = User(name=user.name, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User registered successfully"}

# Login endpoint
@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Find user by email
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    return {"message": "Login successful", "email": db_user.email}


@app.post('/extract-for-avatar/')
async def extract_for_avatar(
    video: UploadFile = File(...),
    user_id: str = Form(...),
    avatar_id: str = Form(...),
    audio_id: str = Form(...)
):
    try:
        video_bytes = await video.read()

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
                timeout=60.0  # optional: prevent hanging
            )

        response.raise_for_status()
        return response.json()

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Request failed: {str(e)}"
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"XTTS service error: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Extraction error: {str(e)}"
        )


@app.post("/generate-avatar/")
async def generate_avatar(
    text: str = Form(...),
    user_id: str = Form(...),
    avatar_id: str = Form(...),
    audio_id: str = Form(...)
):
    """
    Step 2: Use extracted data to synthesize voice and generate avatar video
    """
    try:
        # Step 1: Synthesize voice using XTTS
        async with httpx.AsyncClient() as client:
            print("xtts aakkaam")
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
            print("aayi")
            xtts_clone_response.raise_for_status()
            print("aavunnu")
            clone_data = xtts_clone_response.json()
            print('clone kazhinju')
            print(clone_data)
            if not clone_data.get("success", False):
                raise HTTPException(status_code=500, detail="Voice Synthesis Failed.")

        # Step 2: Generate avatar video with SadTalker
        async with httpx.AsyncClient() as client:
            print("keri4")
            sadtalker_response = await client.post(
                "http://127.0.0.1:8002/create-avatar/",
                data={
                    "audio_id": audio_id,
                    "user_id": user_id,
                    "avatar_id": avatar_id
                },
                timeout=3600
            )
            print('erangi')
            sadtalker_response.raise_for_status()
            video_data = sadtalker_response.json()

            print("keri5")
            return FileResponse(
    path=video_data["video_path"],
    media_type="video/mp4"
)


    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Synthesis/Avatar generation service error: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Avatar generation error: {str(e)}"
        )