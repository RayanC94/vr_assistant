import os
import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "medical_instruments"


def get_collection():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY manquant. Ajoute-le dans .env.")

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    embed_fn = embedding_functions.OpenAIEmbeddingFunction(
        api_key=api_key,
        model_name="text-embedding-3-small"
    )

    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn
    )
