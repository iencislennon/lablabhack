"""
base_agent.py — Base class for all agents.
Combines: Featherless AI (LLM) + ChromaDB (RAG) + Band SDK (coordination).
"""

import os
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parents[2] / ".env")
from openai import AsyncOpenAI
from loguru import logger

from backend.config import AGENT_MODELS, AGENT_MODELS_FALLBACK, SYSTEM_PROMPTS, RAG_QUERIES
from backend.vector_db.setup import query_collection



def _make_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=os.getenv("FEATHERLESS_API_KEY"),
        base_url=os.getenv("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1"),
    )


class BaseAgent:
    """
    Base class shared by all five agents.

    Execution flow:
    1. RAG query to ChromaDB  → retrieve relevant context documents
    2. Build prompt with RAG context injected into system message
    3. Call Featherless AI (OpenAI-compatible API) — tries primary model, falls back if needed
    4. Parse JSON response into a Pydantic model
    5. Publish result to Band Room via thenvoi SDK
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.model = AGENT_MODELS[agent_name]
        self.model_fallback = AGENT_MODELS_FALLBACK[agent_name]
        self.system_prompt = SYSTEM_PROMPTS[agent_name]
        self.rag_queries = RAG_QUERIES[agent_name]
        self.llm = _make_client()
        logger.info(f"[{agent_name}] initialised | primary={self.model}")

    async def get_rag_context(self) -> tuple[list[str], str]:
        """
        Retrieve relevant context from ChromaDB.
        Returns (source_ids, formatted context string).
        Falls back gracefully if the collection is empty.
        """
        try:
            docs = query_collection(self.agent_name, self.rag_queries, n_results=5)
        except Exception as e:
            logger.warning(f"[{self.agent_name}] ChromaDB query failed: {e}")
            return [], "No historical data available — use general knowledge."

        if not docs:
            logger.warning(f"[{self.agent_name}] Collection empty — run seed_data.py first")
            return [], "No historical data available — use general knowledge."

        sources = [f"doc_{i+1}" for i in range(len(docs))]
        context = "\n\n".join(f"[Source {i+1}]:\n{doc}" for i, doc in enumerate(docs))
        logger.info(f"[{self.agent_name}] RAG: {len(docs)} docs loaded")
        return sources, context

    async def _call_model(self, model: str, system: str, user: str) -> str:
        """Single LLM call. Returns raw string content."""
        response = await self.llm.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            temperature=0.2,
            max_tokens=2048,
        )
        return response.choices[0].message.content.strip()

    async def run_llm(self, user_message: str, context: str) -> dict:
        """
        Call Featherless AI with primary model; fall back to smaller model on error.
        Returns a parsed JSON dict.
        """
        system = f"""{self.system_prompt}

KNOWLEDGE BASE (ChromaDB RAG):
{context}
"""
        raw = None
        for model in [self.model, self.model_fallback]:
            try:
                logger.info(f"[{self.agent_name}] Calling {model}...")
                raw = await self._call_model(model, system, user_message)
                break
            except Exception as e:
                logger.warning(f"[{self.agent_name}] Model {model} failed: {e} — trying fallback")

        if raw is None:
            raise RuntimeError(f"[{self.agent_name}] All models failed")

        # Strip markdown fences if model ignored the instruction
        if "```" in raw:
            parts = raw.split("```")
            for part in parts:
                candidate = part.strip().lstrip("json").strip()
                if candidate.startswith("{"):
                    raw = candidate
                    break

        # Find the first JSON object in the response
        start = raw.find("{")
        end   = raw.rfind("}") + 1
        if start >= 0 and end > start:
            raw = raw[start:end]

        try:
            result = json.loads(raw)
            logger.info(f"[{self.agent_name}] JSON parsed OK")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"[{self.agent_name}] JSON parse error: {e}\nRaw: {raw[:400]}")
            raise ValueError(f"Agent {self.agent_name} returned invalid JSON: {e}")

    async def analyze(self, scenario: str) -> dict:
        """
        Main entry point: RAG → LLM → raw dict.
        Subclasses override this to add Pydantic validation.
        """
        sources, context = await self.get_rag_context()

        user_message = f"""Scenario:
{scenario}

Use the knowledge base documents above.
Populate rag_sources with: {sources}
Return ONLY the JSON object — no other text."""

        result = await self.run_llm(user_message, context)
        result["rag_sources"] = sources
        return result