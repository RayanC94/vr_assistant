import os
import json
from openai import OpenAI
from app.prompts import INTENT_PROMPT, ANSWER_RULES

_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


def classify_intent(transcript: str, target_object_name: str | None, mode: str) -> dict:
    prompt = INTENT_PROMPT.format(
        transcript=transcript,
        target_object_name=target_object_name or "null",
        mode=mode
    )

    resp = _client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Réponds en JSON strict, sans texte additionnel."},
            {"role": "user", "content": prompt},
        ],
        temperature=0
    )

    raw = (resp.choices[0].message.content or "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "intent": "OUT_OF_SCOPE",
            "confidence": "low",
            "equipment_mentioned": None,
            "raw": raw
        }


def generate_answer(
    transcript: str,
    mode: str,
    intent: str,
    context: dict,
    sources: list[dict]
) -> str:
    sources_block = ""
    if sources:
        formatted = []
        for s in sources:
            meta = s.get("metadata", {})
            title = meta.get("equipment_name") or meta.get("source_file") or "Source"
            formatted.append(f"[Source: {title} | {meta.get('source_file','')}]\\n{s.get('text','')}")
        sources_block = "\n\n".join(formatted)
    else:
        sources_block = "Aucune source interne disponible."

    user_msg = f"""
Question: {transcript}

Contexte (résumé): {json.dumps(context, ensure_ascii=False)}

SOURCES:
{sources_block}

Consignes:
- Si SOURCES présentes: cite la source en fin de phrase, ex: (Source: Bistouri électrique).
- Si aucune source: dis-le explicitement.
"""

    system = ANSWER_RULES
    if mode == "Jeu" and intent == "HINT_GAME":
        system += "\nRappel mode Jeu: donne un INDICE, pas la solution complète."

    resp = _client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2
    )

    return (resp.choices[0].message.content or "").strip()
