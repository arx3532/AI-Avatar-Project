import subprocess
import os
import sqlite3
import json
import numpy as np
import torch
import torchaudio

def run_sadtalker(cloned_audio_output: str,input_image: str, result_dir:str):
    command = [
        "py", "inference.py",
        "--driven_audio", cloned_audio_output,
        "--source_image", input_image,
        "--result_dir", result_dir,
        "--enhancer", "gfpgan"
    ]
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    subprocess.run(command)

def load_image_from_db(user_id: str, avatar_id: str, db_path='../shared/avatar-database.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT image_blob, image_shape FROM avatar_frames WHERE user_id = ? and avatar_id = ?", 
              (user_id, avatar_id))
    result = c.fetchone()
    conn.close()

    if result:
        blob, shape = result
        shape = tuple(json.loads(shape))
        image_np = np.frombuffer(blob, dtype=np.uint8).reshape(shape)
        return image_np
    
    else:
        raise ValueError(f"No image found in DB for user {user_id}")

def load_audio(user_id, audio_id):
    conn = sqlite3.connect('../shared/avatar-database.db')
    c = conn.cursor()
    c.execute(
        """
    SELECT audio_blob,audio_shape,sample_rate FROM speaker_embed where user_id = ? and audio_id = ?   
        """,(user_id, audio_id)
    )
    result = c.fetchone()
    conn.close()
    if result:
        audio_blob, audio_shape, sample_rate = result
        audio_shape = tuple(json.loads(audio_shape))
        audio_np = np.frombuffer(audio_blob, dtype=np.float32).reshape(audio_shape)
        audio_np = audio_np.copy()
        audio_tensor = torch.from_numpy(audio_np)
        temp_audio_path = "../shared/temp_audio.wav"
        torchaudio.save(temp_audio_path, audio_tensor, sample_rate)
        return temp_audio_path
    else:
        print("Data Not Found. Try Creating One.")
        return
