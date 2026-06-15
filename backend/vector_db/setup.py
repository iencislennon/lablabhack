"""
vector_db/setup.py — ChromaDB collection initialisation for each agent.
"""

import chromadb
import os
from chromadb.utils import embedding_functions
from loguru import logger


def get_chroma_client() -> chromadb.PersistentClient:
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
    os.makedirs(persist_dir, exist_ok=True)
    return chromadb.PersistentClient(path=persist_dir)


def get_embedding_function():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )


COLLECTION_NAMES = {
    "farmer":    "farmers_collection",
    "logistics": "logistics_collection",
    "energy":    "energy_collection",
    "market":    "market_collection",
    "regulator": "regulator_collection",
}


def get_or_create_collection(agent_name: str) -> chromadb.Collection:
    client = get_chroma_client()
    ef = get_embedding_function()
    collection_name = COLLECTION_NAMES[agent_name]

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=ef,
        metadata={"agent": agent_name, "hnsw:space": "cosine"},
    )
    logger.info(f"Collection '{collection_name}' ready ({collection.count()} docs)")
    return collection


def query_collection(agent_name: str, queries: list[str], n_results: int = 5) -> list[str]:
    """
    RAG query against an agent's collection.
    Returns a list of relevant document texts.
    """
    collection = get_or_create_collection(agent_name)

    if collection.count() == 0:
        logger.warning(f"Collection '{agent_name}' is empty — no RAG context available")
        return []

    results = collection.query(
        query_texts=queries,
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    docs = []
    seen = set()
    for doc_list, meta_list, dist_list in zip(
        results["documents"], results["metadatas"], results["distances"]
    ):
        for doc, meta, dist in zip(doc_list, meta_list, dist_list):
            # Filter by cosine distance threshold to keep only relevant results
            if doc not in seen and dist < 0.7:
                docs.append(doc)
                seen.add(doc)

    logger.info(f"RAG [{agent_name}]: {len(docs)} relevant docs retrieved")
    return docs


def add_documents(agent_name: str, documents: list[dict]):
    """
    Add documents to an agent's collection.
    documents: [{"id": "...", "text": "...", "metadata": {...}}]
    """
    collection = get_or_create_collection(agent_name)
    collection.add(
        ids=[d["id"] for d in documents],
        documents=[d["text"] for d in documents],
        metadatas=[d.get("metadata", {}) for d in documents],
    )
    logger.info(f"Added {len(documents)} docs to '{agent_name}' collection")


if __name__ == "__main__":
    for agent in COLLECTION_NAMES:
        get_or_create_collection(agent)
    print("✅ All ChromaDB collections initialised")