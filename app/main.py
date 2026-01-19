import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.health import router as health_router
from app.routes.rag_index import router as rag_router
from app.routes.ask import router as ask_router
from app.routes.voice import router as voice_router
from app.routes.voice_turn import router as voice_turn_router
from app.routes.voice_turn_json import router as voice_turn_json_router


app = FastAPI(title="VR Assistant API", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OK en dev, en prod on restreint
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(rag_router)
app.include_router(ask_router)
app.include_router(voice_router)
app.include_router(voice_turn_router)
app.include_router(voice_turn_json_router)
