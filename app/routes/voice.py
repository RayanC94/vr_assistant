import os
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import Response
from openai import OpenAI

router = APIRouter()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@router.post("/voice/transcribe")
async def voice_transcribe(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    tr = client.audio.transcriptions.create(
        model="gpt-4o-transcribe",
        file=(file.filename, audio_bytes, file.content_type or "application/octet-stream"),
    )
    return {"transcript": tr.text}

@router.post("/voice/tts")
async def voice_tts(payload: dict):
    text = (payload.get("text") or "").strip()
    if not text:
        return {"error": "text vide"}

    audio = client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="alloy",
    input=text,
    response_format="mp3"
    )
    # Selon le SDK, audio peut être un flux binaire direct ou un objet.
    # Le plus robuste : récupérer les bytes via .read() si dispo, sinon via audio
    content = audio.read() if hasattr(audio, "read") else audio

    return Response(content=content, media_type="audio/mpeg")
