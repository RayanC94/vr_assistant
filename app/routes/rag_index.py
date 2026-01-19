from fastapi import APIRouter
from app.rag.ingest import index_markdown_docs

router = APIRouter()

@router.post("/index")
def index_docs():
    return index_markdown_docs()
