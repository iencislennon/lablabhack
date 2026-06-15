"""
launch_all_band_agents.py — Start all 5 agents as persistent Band participants.

Each agent connects to the Band platform via WebSocket and listens for messages.
Run this BEFORE starting the FastAPI server.

Usage:
    python launch_all_band_agents.py
"""

import asyncio
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


async def main():
    from backend.agents.farmer import run_farmer_band_agent
    from backend.agents.logistics import run_logistics_band_agent
    from backend.agents.energy import run_energy_band_agent
    from backend.agents.market import run_market_band_agent
    from backend.agents.regulator import run_regulator_band_agent

    logger.info("🚀 Launching all 5 Band agents in parallel...")
    logger.info("Each agent will connect to the Band platform via WebSocket.")
    logger.info("Press Ctrl+C to stop all agents.\n")

    tasks = [
        asyncio.create_task(run_farmer_band_agent(),    name="farmer"),
        asyncio.create_task(run_logistics_band_agent(), name="logistics"),
        asyncio.create_task(run_energy_band_agent(),    name="energy"),
        asyncio.create_task(run_market_band_agent(),    name="market"),
        asyncio.create_task(run_regulator_band_agent(), name="regulator"),
    ]

    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("Shutting down all agents...")
        for task in tasks:
            task.cancel()


if __name__ == "__main__":
    asyncio.run(main())
