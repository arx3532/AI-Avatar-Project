import subprocess
import torchaudio
import torch
import sqlite3
import json
import numpy as np
import os

def extract_audio(input_video: str, output_audio: str):
    command = ['ffmpeg', '-i', input_video, '-map', 'a', output_audio, '-y']
    subprocess.run(command, check=True)

def save_audio(wav_tensor, path: str, sample_rate: int = 24000):
    torchaudio.save(path, torch.tensor(wav_tensor).unsqueeze(0), sample_rate)

def save_to_db(user_id, reference_audio_path):
    audio_blob, audio_shape, sample_rate = audio_to_numpy(reference_audio_path)
    conn = sqlite3.connect('voice-clone.db')
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS speaker_embed (
            user_id TEXT,
            audio_blob BLOB,
            audio_shape TEXT,
            sample_rate INTEGER
            )
    """)

    c.execute("""REPLACE INTO speaker_embed (user_id, audio_blob,audio_shape,sample_rate) 
            VALUES (?, ?, ?, ?)""",(user_id, audio_blob,json.dumps(audio_shape), sample_rate))

    conn.commit()
    conn.close()

def audio_to_numpy(reference_audio_path):
    try:
        waveform, sample_rate =torchaudio.load(reference_audio_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load audio: {e}")
    audio_np = waveform.numpy()
    audio_blob = audio_np.tobytes()
    audio_shape = audio_np.shape
    return audio_blob,audio_shape, sample_rate

def clone_audio(model,user_id,gen_text,output_audio_path):
    conn = sqlite3.connect('voice-clone.db')
    c = conn.cursor()
    c.execute(
        """
    SELECT audio_blob,audio_shape,sample_rate FROM speaker_embed where user_id = ?    
        """,(user_id,)
    )
    result = c.fetchone()
    conn.close()
    if result:
        audio_blob, audio_shape, sample_rate = result
        audio_shape = tuple(json.loads(audio_shape))
        audio_np = np.frombuffer(audio_blob, dtype=np.float32).reshape(audio_shape)
        audio_np = audio_np.copy()
        audio_tensor = torch.from_numpy(audio_np)
        temp_audio_path = "temp_audio.wav"
        torchaudio.save(temp_audio_path, audio_tensor, sample_rate)

    else:
        print("Data Not Found. Try Creating One.")
        return
    gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(audio_path = temp_audio_path)
    out = model.inference(
        gen_text,
        "en",
        gpt_cond_latent,
        speaker_embedding,
        temperature=0.7, 
    )
    save_audio(out["wav"], output_audio_path)
    os.remove(temp_audio_path)
    print(f"Speech generated and saved to {output_audio_path}")




