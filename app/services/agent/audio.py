import io
import openai

from fastapi import UploadFile

from app.core.config import settings


async def transcribe_audio(audio_file: UploadFile) -> str:
    """
    Транскрибация аудио через OpenAI Whisper API.
    """
    buffer = io.BytesIO(await audio_file.read())
    buffer.name = "audio.mp3"

    # клиент openai напрямую для whisper
    client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    transcript = await client.audio.transcriptions.create(
        model="whisper-1", file=buffer
    )

    return transcript.text
