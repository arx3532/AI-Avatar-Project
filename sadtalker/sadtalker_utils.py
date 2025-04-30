import subprocess
import os
def run_sadtalker(cloned_audio_output: str,input_image: str, result_dir:str):
    command = [
        "python", "inference.py",
        "--driven_audio", cloned_audio_output,
        "--source_image", input_image,
        "--result_dir", result_dir,
        "--enhancer", "gfpgan"
    ]
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    subprocess.run(command)
