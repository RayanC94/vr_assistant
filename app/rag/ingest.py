import os
import glob
from app.rag.chroma_store import get_collection

DOCS_PATH = "data/docs"


def parse_frontmatter(md_text: str) -> tuple[dict, str]:
    meta = {}
    body = md_text

    if md_text.startswith("---"):
        end = md_text.find("\n---", 3)
        if end != -1:
            block = md_text[3:end].strip()
            for line in block.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"')
            body = md_text[end + 4:].strip()

    return meta, body


def smart_chunk_markdown(md_body: str) -> list[str]:
    # Chunking simple par sections (##) avec fallback
    parts = []
    current = []
    lines = md_body.splitlines()

    for line in lines:
        if line.startswith("## "):
            if current:
                parts.append("\n".join(current).strip())
                current = []
        current.append(line)

    if current:
        parts.append("\n".join(current).strip())

    # Si trop peu de sections, fallback en chunks de taille fixe
    if len(parts) <= 1:
        return char_chunks(md_body)

    # Nettoyage: supprimer trop petits
    cleaned = [p for p in parts if len(p) > 120]
    return cleaned if cleaned else char_chunks(md_body)


def char_chunks(text: str, max_chars: int = 1800, overlap: int = 250) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + max_chars)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def index_markdown_docs() -> dict:
    collection = get_collection()

    files = glob.glob(os.path.join(DOCS_PATH, "*.md"))
    if not files:
        return {"indexed": 0, "message": "Aucun .md trouvé dans data/docs"}

    indexed = 0

    for fp in files:
        with open(fp, "r", encoding="utf-8") as f:
            raw = f.read()

        meta, body = parse_frontmatter(raw)
        equipment_name = meta.get("equipment_name") or os.path.basename(fp)
        chunks = smart_chunk_markdown(body)

        for i, ch in enumerate(chunks):
            doc_id = f"{os.path.basename(fp)}::chunk{i}"
            collection.upsert(
                documents=[ch],
                metadatas=[{
                    "source_file": os.path.basename(fp),
                    "equipment_name": equipment_name,
                    **meta
                }],
                ids=[doc_id]
            )
            indexed += 1

    return {"indexed": indexed, "message": "Indexation terminée."}
