from fastapi import APIRouter
from app.schemas import AskRequest, AskResponse, Citation
from app.llm_agent import classify_intent, generate_answer
from app.rag.retrieve import retrieve

router = APIRouter()

@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    ctx = req.vr_context.model_dump()

    intent_data = classify_intent(
        transcript=req.transcript,
        target_object_name=req.vr_context.target_object_name,
        mode=req.mode
    )

    intent = intent_data.get("intent", "OUT_OF_SCOPE")
    confidence = intent_data.get("confidence", "low")

    equipment_hint = intent_data.get("equipment_mentioned") or req.vr_context.target_object_name

    sources = []
    if intent in ("INFO_EQUIPMENT", "USAGE_PRECAUTIONS", "HINT_GAME"):
        sources = retrieve(req.transcript, k=4, equipment_hint=equipment_hint)

    assistant_text = generate_answer(
        transcript=req.transcript,
        mode=req.mode,
        intent=intent,
        context={
            "user_profile": req.user_profile,
            "mode": req.mode,
            "vr_context": ctx
        },
        sources=sources
    )

    citations = []
    for s in sources:
        meta = s.get("metadata", {})
        citations.append(Citation(
            source_file=meta.get("source_file"),
            equipment_name=meta.get("equipment_name"),
            validated_by=meta.get("validated_by"),
            last_reviewed_date=meta.get("last_reviewed_date"),
            chunk_id=s.get("id")
        ))

    return AskResponse(
        assistant_text=assistant_text,
        intent=intent,
        confidence=confidence,
        citations=citations
    )
