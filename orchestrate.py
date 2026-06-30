"""DevDuo — end-to-end orchestration.

Runs the BE Agent to build an API and post its contract to crosstalk-mcp,
then runs the FE Agent to read that contract and build a matching UI.

Usage:
    source .venv/bin/activate
    python orchestrate.py "Build me a TODO app"
"""

import asyncio
import sys

from google.adk.runners import InMemoryRunner

from be_agent.agent import root_agent as be_root_agent
from fe_agent.agent import root_agent as fe_root_agent


async def run_agent(agent, prompt: str, label: str) -> None:
    print(f"\n{'=' * 60}\n  {label}\n{'=' * 60}")
    runner = InMemoryRunner(agent=agent, app_name=f"devduo-{agent.name}")
    events = await runner.run_debug(prompt, user_id="devduo-user")
    for event in events:
        if event.content and event.content.parts:
            for part in event.content.parts:
                if getattr(part, "text", None):
                    print(part.text)
    await runner.close()


async def main() -> None:
    feature = " ".join(sys.argv[1:]) or "Build me a TODO app"

    # Deliberately sequential, not parallel: the FE agent's prompt only tells
    # it the contract exists, not what it says. It has to fetch the contract
    # itself off crosstalk-mcp (see fe_agent/agent.py) — this orchestrator
    # never passes API details between the two agents directly, so the relay
    # really is the only integration path, not just a formality.
    await run_agent(
        be_root_agent,
        f"Feature request from the user: {feature}",
        "BE Agent",
    )
    await run_agent(
        fe_root_agent,
        f"The BE Agent has posted a contract for this feature request: {feature}. "
        "Read it from the crosstalk relay and build the frontend.",
        "FE Agent",
    )

    print(f"\n{'=' * 60}\n  Done. See be_agent/output/ and fe_agent/output/\n{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(main())
