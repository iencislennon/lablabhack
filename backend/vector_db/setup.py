"""
vector_db/setup.py — ChromaDB collection initialisation for each agent.
Uses DefaultEmbeddingFunction (onnxruntime-based, ~50MB) instead of
SentenceTransformer (torch-based, ~1.5GB) to stay within Render free tier memory.
"""

import chromadb
import os
from chromadb.utils import embedding_functions
from loguru import logger

_client = None
_ef = None
_collections: dict = {}


def get_chroma_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        os.makedirs(persist_dir, exist_ok=True)
        _client = chromadb.PersistentClient(path=persist_dir)
        logger.info("ChromaDB client initialised")
    return _client


def get_embedding_function():
    global _ef
    if _ef is None:
        # DefaultEmbeddingFunction uses onnxruntime (~50MB) not torch (~1.5GB)
        # Safe for Render free tier (512MB RAM limit)
        _ef = embedding_functions.DefaultEmbeddingFunction()
        logger.info("Embedding function loaded (DefaultEmbeddingFunction / onnxruntime)")
    return _ef


COLLECTION_NAMES = {
    "farmer":    "farmers_collection",
    "logistics": "logistics_collection",
    "energy":    "energy_collection",
    "market":    "market_collection",
    "regulator": "regulator_collection",
}


def get_or_create_collection(agent_name: str) -> chromadb.Collection:
    global _collections
    if agent_name in _collections:
        return _collections[agent_name]

    client = get_chroma_client()
    ef = get_embedding_function()
    collection_name = COLLECTION_NAMES[agent_name]

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=ef,
        metadata={"agent": agent_name, "hnsw:space": "cosine"},
    )
    _collections[agent_name] = collection
    logger.info(f"Collection '{collection_name}' ready ({collection.count()} docs)")
    return collection


def query_collection(agent_name: str, queries: list[str], n_results: int = 3) -> list[str]:
    """RAG query — returns relevant document texts."""
    collection = get_or_create_collection(agent_name)

    if collection.count() == 0:
        logger.warning(f"Collection '{agent_name}' is empty — run seed_data.py first")
        return []

    results = collection.query(
        query_texts=queries[:2],
        n_results=min(n_results, collection.count()),
        include=["documents", "distances"],
    )

    docs = []
    seen = set()
    for doc_list, dist_list in zip(results["documents"], results["distances"]):
        for doc, dist in zip(doc_list, dist_list):
            if doc not in seen and dist < 0.75:
                docs.append(doc)
                seen.add(doc)

    logger.info(f"RAG [{agent_name}]: {len(docs)} docs retrieved")
    return docs


def add_documents(agent_name: str, documents: list[dict]):
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