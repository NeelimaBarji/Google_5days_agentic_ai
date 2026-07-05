"""
API Test MCP Server
HTTP tools for integration testing — GET, POST, PUT and response verification.

Security:
  - MCP_API_KEY validation on every tool call (set in .env)
"""

import os
from dotenv import load_dotenv

# Load .env so this server works standalone AND under ADK subprocess spawning
load_dotenv()
import httpx
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

MCP_API_KEY = os.environ.get("MCP_API_KEY", "")

app = Server("api-test-mcp")


def _check_auth(arguments: dict) -> "types.TextContent | None":
    if not MCP_API_KEY:
        return None
    if arguments.get("api_key") != MCP_API_KEY:
        return types.TextContent(type="text", text="ERROR: Unauthorized — invalid or missing MCP_API_KEY")
    return None


@app.list_tools()
async def list_tools():
    return [
        types.Tool(name="http_get", description="Make an HTTP GET request", inputSchema={
            "type": "object",
            "properties": {"api_key": {"type": "string", "description": "MCP API key (required)"}, 
                "url": {"type": "string"},
                "params": {"type": "object", "default": {}}
            },
            "required": ["url"]
        }),
        types.Tool(name="http_post", description="Make an HTTP POST request", inputSchema={
            "type": "object",
            "properties": {"api_key": {"type": "string", "description": "MCP API key (required)"}, 
                "url": {"type": "string"},
                "body": {"type": "object"}
            },
            "required": ["url", "body"]
        }),
        types.Tool(name="http_put", description="Make an HTTP PUT request", inputSchema={
            "type": "object",
            "properties": {"api_key": {"type": "string", "description": "MCP API key (required)"}, 
                "url": {"type": "string"},
                "body": {"type": "object"}
            },
            "required": ["url", "body"]
        }),
        types.Tool(name="verify_response", description="Verify a JSON response contains expected fields/values", inputSchema={
            "type": "object",
            "properties": {"api_key": {"type": "string", "description": "MCP API key (required)"}, 
                "response_json": {"type": "string", "description": "JSON string of the response"},
                "expected_fields": {"type": "array", "items": {"type": "string"}, "description": "Field names that must exist"},
                "expected_values": {"type": "object", "description": "Field:value pairs that must match"}
            },
            "required": ["response_json", "expected_fields"]
        }),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    # ── Security: API key check ──────────────────────────────────────────────
    auth_err = _check_auth(arguments)
    if auth_err:
        return [auth_err]

    async with httpx.AsyncClient(timeout=10.0) as client:

        if name == "http_get":
            try:
                r = await client.get(arguments["url"], params=arguments.get("params", {}))
                return [types.TextContent(type="text", text=json.dumps({
                    "status_code": r.status_code,
                    "body": r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text
                }, indent=2))]
            except Exception as e:
                return [types.TextContent(type="text", text=f"ERROR: {str(e)}")]

        elif name == "http_post":
            try:
                r = await client.post(arguments["url"], json=arguments["body"])
                return [types.TextContent(type="text", text=json.dumps({
                    "status_code": r.status_code,
                    "body": r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text
                }, indent=2))]
            except Exception as e:
                return [types.TextContent(type="text", text=f"ERROR: {str(e)}")]

        elif name == "http_put":
            try:
                r = await client.put(arguments["url"], json=arguments["body"])
                return [types.TextContent(type="text", text=json.dumps({
                    "status_code": r.status_code,
                    "body": r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text
                }, indent=2))]
            except Exception as e:
                return [types.TextContent(type="text", text=f"ERROR: {str(e)}")]

        elif name == "verify_response":
            try:
                data = json.loads(arguments["response_json"])
                body = data.get("body", data)
                results = []

                # Check status code if present
                if "status_code" in data and data["status_code"] not in (200, 201):
                    return [types.TextContent(type="text", text=f"FAIL: HTTP {data['status_code']}")]

                # Check expected fields
                if isinstance(body, list):
                    sample = body[0] if body else {}
                else:
                    sample = body

                for field in arguments.get("expected_fields", []):
                    if field in sample:
                        results.append(f"✅ Field '{field}' present: {sample[field]}")
                    else:
                        results.append(f"❌ Field '{field}' MISSING")

                # Check expected values
                for field, expected in arguments.get("expected_values", {}).items():
                    actual = sample.get(field)
                    if actual == expected:
                        results.append(f"✅ '{field}' = {expected}")
                    else:
                        results.append(f"❌ '{field}': expected {expected}, got {actual}")

                overall = "PASS" if all("✅" in r for r in results) else "FAIL"
                return [types.TextContent(type="text", text=f"Verification: {overall}\n" + "\n".join(results))]
            except Exception as e:
                return [types.TextContent(type="text", text=f"ERROR in verify: {str(e)}")]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
