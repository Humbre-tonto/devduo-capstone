"""DevDuo — BE Agent.

Analyzes a feature request, picks a backend stack, writes the API code to
./output, and posts the integration contract to the crosstalk-mcp relay on
the BE_TO_FE_CHANNEL so the FE Agent can pick it up.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

RELAY_URL = os.environ["RELAY_URL"]
RELAY_TOKEN = os.environ["RELAY_TOKEN"]
BE_TO_FE_CHANNEL = os.environ.get("BE_TO_FE_CHANNEL", "be-to-fe")


def write_file(relative_path: str, content: str) -> dict:
    """Write a file under the BE agent's output directory.

    relative_path: path relative to be_agent/output, e.g. "main.py".
    content: full file contents to write.
    """
    target = (OUTPUT_DIR / relative_path).resolve()
    if OUTPUT_DIR not in target.parents and target != OUTPUT_DIR:
        return {"error": "path escapes output directory"}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    return {"written": str(target.relative_to(OUTPUT_DIR))}


crosstalk_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=f"{RELAY_URL}/mcp",
        headers={"Authorization": f"Bearer {RELAY_TOKEN}"},
    ),
)

root_agent = LlmAgent(
    name="be_agent",
    model="gemini-2.5-flash",
    description="Backend developer agent that builds an API and publishes its contract.",
    instruction=f"""You are the Backend Developer agent in the DevDuo system.

Given a feature request from the user, you must:
1. Decide on a backend stack (default: Python FastAPI unless the request demands otherwise).
2. Design the REST API: endpoints, request/response schema, base URL (assume
   http://localhost:8000 for local dev).
3. Write the full working backend code using the write_file tool. Always include
   a requirements.txt and a main.py that runs with `uvicorn main:app`. Use an
   in-memory data store unless told otherwise — this is a demo.
4. Once the code is written, call the crosstalk post_message tool with:
   - channel: "{BE_TO_FE_CHANNEL}"
   - sender: "be-agent"
   - type: "CONTRACT"
   - body: a JSON string describing {{"endpoints": [...], "schema": {{...}}, "base_url": "..."}}
5. After posting, reply to the user with a short summary of what you built and
   confirm the contract was posted.

Do not wait for a response on this channel — your job ends once the contract is posted.
""",
    tools=[write_file, crosstalk_toolset],
)
