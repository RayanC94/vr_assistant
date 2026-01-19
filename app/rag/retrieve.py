from app.rag.chroma_store import get_collection


def retrieve(query: str, k: int = 4, equipment_hint: str | None = None) -> list[dict]:
    collection = get_collection()

    where = None
    if equipment_hint:
        where = {"equipment_name": equipment_hint}

    res = collection.query(
        query_texts=[query],
        n_results=k,
        where=where
    )

    docs = []
    docs_list = res.get("documents", [[]])[0]
    metas_list = res.get("metadatas", [[]])[0]
    ids_list = res.get("ids", [[]])[0]

    for i in range(len(docs_list)):
        docs.append({
            "text": docs_list[i],
            "metadata": metas_list[i],
            "id": ids_list[i]
        })

    return docs
