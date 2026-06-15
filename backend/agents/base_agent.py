"""
base_agent.py — Base class for all agents.
Combines: Featherless AI (LLM) + ChromaDB (RAG) + Band SDK (coordination).
"""

import os
import json
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from loguru import logger

from backend.config import AGENT_MODELS, SYSTEM_PROMPTS, RAG_QUERIES
from backend.vector_db.setup import query_collection

load_dotenv()


class BaseAgent:
    """
    Base class shared by all five agents.

    Execution flow:
    1. RAG query to ChromaDB  → retrieve relevant context documents
    2. Build prompt with context
    3. Call Featherless AI (OpenAI-compatible API)
    4. Parse JSON response into a Pydantic model
    5. Publish result to Band Room via thenvoi SDK
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.model = AGENT_MODELS[agent_name]
        self.system_prompt = SYSTEM_PROMPTS[agent_name]
        self.rag_queries = RAG_QUERIES[agent_name]

        # Featherless AI — OpenAI-compatible client
        self.llm = AsyncOpenAI(
            api_key=os.getenv("FEATHERLESS_API_KEY"),
            base_url=os.getenv("FEATHERLESS_BASE_URL", "https://api.featherless.ai/v1"),
        )

        logger.info(f"[{agent_name}] Agent initialised | model: {self.model}")

    async def get_rag_context(self) -> tuple[list[str], str]:
        """
        Retrieve relevant context from ChromaDB.
        Returns (source_ids, formatted context string for the prompt).
        """
        docs = query_collection(self.agent_name, self.rag_queries, n_results=5)

        if not docs:
            logger.warning(f"[{self.agent_name}] No RAG context found")
            return [], "Historical data unavailable. Fall back to general knowledge."

        sources = [f"doc_{i+1}" for i in range(len(docs))]
        context = "\n\n".join([
            f"[Source {i+1}]:\n{doc}"
            for i, doc in enumerate(docs)
        ])

        logger.info(f"[{self.agent_name}] RAG: {len(docs)} docs loaded")
        return sources, context

    async def run_llm(self, user_message: str, context: str) -> dict:
        """
        Call Featherless AI with the assembled prompt.
        Returns a parsed JSON dict.
        """
        full_system = f"""{self.system_prompt}

═══ KNOWLEDGE BASE DATA (ChromaDB RAG) ═══
{context}
═══════════════════════════════════════════

CRITICAL: Reply with valid JSON only. No text before or after the JSON object.
"""

        logger.info(f"[{self.agent_name}] Calling Featherless AI ({self.model})...")

        response = await self.llm.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": full_system},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            max_tokens=2048,
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown code fences if the model wrapped the JSON in ```json
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        try:
            result = json.loads(raw)
            logger.info(f"[{self.agent_name}] LLM response parsed successfully")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"[{self.agent_name}] JSON parse error: {e}")
            logger.debug(f"Raw response (first 500 chars): {raw[:500]}")
            raise ValueError(f"Agent {self.agent_name} returned invalid JSON: {e}")

    async def analyze(self, scenario: str) -> dict:
        """
        Main entry point: RAG → LLM → validated JSON dict.
        Subclasses override this to add Pydantic validation.
        """
        sources, context = await self.get_rag_context()

        user_message = f"""
Scenario for analysis:
{scenario}

Use the knowledge base documents provided above.
Return the result as JSON matching your schema.
Populate the rag_sources field with: {sources}
"""

        result = await self.run_llm(user_message, context)
        result["rag_sources"] = sources
        return result

    async def publish_to_band(self, payload: dict, band_agent, room_id: str):
        """
        Publish the result to the Band Room via the thenvoi SDK.
        band_agent — a thenvoi.Agent instance
        """
        message = (
            f"@Coordinator Here is my analysis:\n"
            f"```json\n{json.dumps(payload, ensure_ascii=False, indent=2)}\n```"
        )

        # Band SDK routes the message via its built-in thenvoi_send_message tool
        logger.info(f"[{self.agent_name}] Publishing to Band Room {room_id}")
        return payload