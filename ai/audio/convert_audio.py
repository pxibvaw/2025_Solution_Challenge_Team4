# ai.audio.convert_audio.py
import subprocess
import uuid
from pathlib import Path


def convert_to_wav16k(input_path: str) -> str:
    """
    모든 오디오 파일을
    16kHz mono wav로 변환
    """

    output_path = f"/tmp/{uuid.uuid4()}.wav"

    command = [
        "ffmpeg",
        "-y",
        "-i", input_path,
        "-ar", "16000",
        "-ac", "1",
        output_path
    ]

    subprocess.run(command, check=True)

    return output_path