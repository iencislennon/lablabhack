"""
band/room.py — In-memory Band Room state manager.

Used by the FastAPI pipeline (main.py) as a lightweight pub/sub layer
when running without the live Band platform.
For production Band platform usage, agents connect via thenvoi SDK instead.
"""

import asyncio
from datetime import datetime
from loguru import logger
from backend.schemas import BandRoomState


class BandRoom:
    """
    Lightweight in-memory pub/sub room for the local pipeline.

    Agents call .publish() to post their payload.
    The coordinator reads .state to detect conflicts.
    Connected WebSocket clients receive events via .subscribe().
    """

    def __init__(self, room_id: str = "food-energy-coordination"):
        self.room_id   = room_id
        self.state     = BandRoomState()
        self._queue: asyncio.Queue = asyncio.Queue()
        self._log: list[dict] = []

    def publish(self, agent_name: str, payload) -> None:
        """Agent posts its result to the room."""
        entry = {
            "agent":     agent_name,
            "timestamp": datetime.utcnow().isoformat(),
            "payload":   payload,
        }
        self._log.append(entry)

        # Update shared state
        setattr(self.state, agent_name, payload)

        # Push event to queue (consumed by WebSocket broadcaster)
        self._queue.put_nowait({
            "event": "agent_done",
            "agent": agent_name,
            "data":  payload.model_dump() if hasattr(payload, "model_dump") else payload,
        })
        logger.info(f"[room:{self.room_id}] {agent_name} published")

    async def next_event(self) -> dict:
        """Wait for the next queued event (async generator pattern)."""
        return await self._queue.get()

    def all_primary_agents_ready(self) -> bool:
        """Returns True once farmer, logistics, energy, and market have published."""
        s = self.state
        return all([s.farmer, s.logistics, s.energy, s.market])

    def get_log(self) -> list[dict]:
        """Return the full publish log for audit purposes."""
        return self._log

    def reset(self) -> None:
        """Clear state between pipeline runs."""
        self.state = BandRoomState()
        self._log  = []
        while not self._queue.empty():
            self._queue.get_nowait()
        logger.info(f"[room:{self.room_id}] reset")