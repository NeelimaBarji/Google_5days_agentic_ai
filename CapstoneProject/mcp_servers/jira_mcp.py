"""
Jira MCP Server (mock implementation using local JSON files)
In production, replace with real Jira REST API calls.

Security:
  - MCP_API_KEY validation on every tool call (set in .env)
"""

import os
from dotenv import load_dotenv

# Load .env so this server works standalone AND under ADK subprocess spawning
load_dotenv()
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

MCP_API_KEY = os.environ.get("MCP_API_KEY", "")

app = Server("jira-mcp")
TICKETS_DIR = os.path.join(os.path.dirname(__file__), "..", "jira-tickets")


def _check_auth(arguments: dict) -> "types.TextContent | None":
    if not MCP_API_KEY:
        return None
    if arguments.get("api_key") != MCP_API_KEY:
        return types.TextContent(type="text", text="ERROR: Unauthorized — invalid or missing MCP_API_KEY")
    return None


def get_ticket(ticket_id: str) -> dict:
    """Utility function — also importable by orchestrator."""
    path = os.path.join(TICKETS_DIR, f"{ticket_id}.json")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Ticket not found: {ticket_id}")
    with open(path) as f:
        return json.load(f)


@app.list_tools()
async def list_tools():
    return [
        types.Tool(name="get_ticket", description="Fetch Jira ticket details", inputSchema={
            "type": "object", "properties": {"api_key": {"type": "string", "description": "MCP API key (required)"}, "ticket_id": {"type": "string"}}, "required": ["ticket_id"]
        }),
        types.Tool(name="update_ticket_status", description="Update Jira ticket status", inputSchema={
            "type": "object",
            "properties": {"api_key": {"type": "string", "description": "MCP API key (required)"}, "ticket_id": {"type": "string"}, "status": {"type": "string"}},
            "required": ["ticket_id", "status"]
        }),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    # ── Security: API key check ──────────────────────────────────────────────
    auth_err = _check_auth(arguments)
    if auth_err:
        return [auth_err]

    if name == "get_ticket":
        try:
            ticket = get_ticket(arguments["ticket_id"])
            return [types.TextContent(type="text", text=json.dumps(ticket, indent=2))]
        except FileNotFoundError as e:
            return [types.TextContent(type="text", text=f"ERROR: {e}")]

    elif name == "update_ticket_status":
        ticket_id = arguments["ticket_id"]
        new_status = arguments["status"]
        path = os.path.join(TICKETS_DIR, f"{ticket_id}.json")
        if os.path.exists(path):
            with open(path) as f:
                ticket = json.load(f)
            ticket["status"] = new_status
            with open(path, "w") as f:
                json.dump(ticket, f, indent=2)
            return [types.TextContent(type="text", text=f"Ticket {ticket_id} updated to: {new_status}")]
        return [types.TextContent(type="text", text=f"ERROR: Ticket not found: {ticket_id}")]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
