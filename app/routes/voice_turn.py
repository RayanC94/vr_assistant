import os
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import Response
from openai import OpenAI

from app.llm_agent import classify_intent, generate_answer
from app.rag.retrieve import retrieve

router = APIRouter()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@router.post("/voice/turn")
async def voice_turn(
    file: UploadFile = File(...),
    mode: str = Form("Decouverte"),
    user_profile: str = Form("default"),
    target_object_name: str = Form(""),
):
    audio_bytes = await file.read()

    # 1) Transcription
    tr = client.audio.transcriptions.create(
        model="gpt-4o-transcribe",
        file=(file.filename, audio_bytes, file.content_type or "application/octet-stream"),
    )
    transcript = tr.text

    # 2) Intent
    intent_data = classify_intent(transcript, target_object_name or None, mode)
    intent = intent_data.get("intent", "OUT_OF_SCOPE")

    # 3) Retrieval RAG
    equipment_hint = intent_data.get("equipment_mentioned") or (target_object_name or None)
    sources = []
    if intent in ("INFO_EQUIPMENT", "USAGE_PRECAUTIONS", "HINT_GAME"):
        sources = retrieve(transcript, k=4, equipment_hint=equipment_hint)

    # 4) Answer
    answer_text = generate_answer(
        transcript=transcript,
        mode=mode,
        intent=intent,
        context={"user_profile": user_profile, "vr_context": {"target_object_name": target_object_name}},
        sources=sources
    )

    # 5) TTS
    audio_resp = client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="alloy",
    input=answer_text,
    response_format="mp3"
    )
    audio_out = audio_resp.read() if hasattr(audio_resp, "read") else audio_resp

    return Response(content=audio_out, media_type="audio/mpeg")
