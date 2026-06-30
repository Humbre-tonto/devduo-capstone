"""DevDuo — FE Agent.

Reads the API contract posted by the BE Agent on the crosstalk-mcp relay,
picks a compatible UI stack, writes the frontend code to ./output, and
posts a confirmation back on the FE_TO_BE_CHANNEL.
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
FE_TO_BE_CHANNEL = os.environ.get("FE_TO_BE_CHANNEL", "fe-to-be")


def write_file(relative_path: str, content: str) -> dict:
    """Write a file under the FE agent's output directory.

    relative_path: path relative to fe_agent/output, e.g. "src/App.jsx".
    content: full file contents to write.
    """
    target = (OUTPUT_DIR / relative_path).resolve()
    # Same sandbox guard as the BE agent: the model picks relative_path, so
    # reject any "../" escape rather than trust it.
    if OUTPUT_DIR not in target.parents and target != OUTPUT_DIR:
        return {"error": "path escapes output directory"}
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    return {"written": str(target.relative_to(OUTPUT_DIR))}


# The FE agent's only source of truth about the API is whatever the BE agent
# posted to be-to-fe through this same relay connection — it never reads the
# BE agent's source files or shares any other context with it.
crosstalk_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=f"{RELAY_URL}/mcp",
        headers={"Authorization": f"Bearer {RELAY_TOKEN}"},
    ),
)

root_agent = LlmAgent(
    name="fe_agent",
    model="gemini-2.5-flash",
    description="Frontend developer agent that consumes a BE contract and builds a matching UI.",
    instruction=f"""You are the Frontend Developer agent in the DevDuo system.

You must:
1. Call the crosstalk get_messages tool with channel "{BE_TO_FE_CHANNEL}" and
   since_id 0 to fetch the API contract posted by the BE agent. The most
   recent message of type CONTRACT has a JSON body describing endpoints,
   schema, and base_url.
2. Decide on a compatible UI stack (default: a single-file React app using
   fetch/axios against the contract's base_url, unless the request demands
   otherwise).
3. Write the full working frontend code using the write_file tool — enough
   to list, add, and delete/toggle items via the contract's endpoints.
   Keep it to a small number of files (e.g. index.html, src/App.jsx,
   package.json).
4. Once the code is written, call the crosstalk post_message tool with:
   - channel: "{FE_TO_BE_CHANNEL}"
   - sender: "fe-agent"
   - type: "CONFIRM"
   - body: a JSON string like {{"status": "ready", "consumed_endpoints": [...], "notes": "..."}}
5. Reply to the user with a short summary of what you built and confirm the
   confirmation was posted.

If no CONTRACT message exists yet on the channel, tell the user the BE agent
hasn't posted a contract yet and stop.
""",
    tools=[write_file, crosstalk_toolset],
)
