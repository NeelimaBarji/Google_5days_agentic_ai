"""
Codebase MCP Server
Exposes file read/write and test execution tools to ADK agents.

Security:
  - MCP_API_KEY validation on every tool call (set in .env)
  - Path traversal prevention via safe_path() — rejects any path escaping PROJECT_ROOT
"""

import os
from dotenv import load_dotenv

# Load .env so this server works standalone AND under ADK subprocess spawning
load_dotenv()
import subprocess
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

PROJECT_ROOT = os.environ.get("PROJECT_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
MCP_API_KEY = os.environ.get("MCP_API_KEY", "")

app = Server("codebase-mcp")


def _check_auth(arguments: dict) -> "types.TextContent | None":
    """Return an error TextContent if the API key is invalid, else None."""
    if not MCP_API_KEY:
        return None  # Key not configured — skip check in dev mode
    if arguments.get("api_key") != MCP_API_KEY:
        return types.TextContent(type="text", text="ERROR: Unauthorized — invalid or missing MCP_API_KEY")
    return None


def safe_path(base: str, requested: str) -> str:
    """
    Resolve `requested` relative to `base` and verify it stays inside `base`.
    Raises ValueError on path traversal attempts (e.g. '../../etc/passwd').
    """
    resolved = os.path.realpath(os.path.join(base, requested))
    if not resolved.startswith(os.path.realpath(base)):
        raise ValueError(f"Path traversal detected: '{requested}' escapes project root")
    return resolved


@app.list_tools()
async def list_tools():
    return [
        types.Tool(name="read_file", description="Read a file from the project", inputSchema={
            "type": "object",
            "properties": {"api_key": {"type": "string", "description": "MCP API key (required)"}, 
                "path": {"type": "string"}
            },
            "required": ["path"]
        }),
        types.Tool(name="write_file", description="Write content to a file", inputSchema={
            "type": "object",
            "properties": {"api_key": {"type": "string", "description": "MCP API key (required)"}, 
                "path": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["path", "content"]
        }),
        types.Tool(name="list_files", description="List files in a directory", inputSchema={
            "type": "object",
            "properties": {"api_key": {"type": "string", "description": "MCP API key (required)"}, 
                "directory": {"type": "string"}
            },
            "required": ["directory"]
        }),
        types.Tool(name="run_maven_tests", description="Run mvn test in backend directory", inputSchema={
            "type": "object", "properties": {"api_key": {"type": "string", "description": "MCP API key (required)"}, }
        }),
        types.Tool(name="run_frontend_tests", description="Run npm test in frontend directory", inputSchema={
            "type": "object", "properties": {"api_key": {"type": "string", "description": "MCP API key (required)"}, }
        }),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    # ── Security: API key check ──────────────────────────────────────────────
    auth_err = _check_auth(arguments)
    if auth_err:
        return [auth_err]

    if name == "read_file":
        try:
            path = safe_path(PROJECT_ROOT, arguments["path"])
        except ValueError as e:
            return [types.TextContent(type="text", text=f"ERROR: {e}")]
        if not os.path.exists(path):
            return [types.TextContent(type="text", text=f"ERROR: File not found: {arguments['path']}")]
        with open(path, "r") as f:
            return [types.TextContent(type="text", text=f.read())]

    elif name == "write_file":
        try:
            path = safe_path(PROJECT_ROOT, arguments["path"])
        except ValueError as e:
            return [types.TextContent(type="text", text=f"ERROR: {e}")]
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(arguments["content"])
        return [types.TextContent(type="text", text=f"Written: {arguments['path']}")]

    elif name == "list_files":
        try:
            directory = safe_path(PROJECT_ROOT, arguments["directory"])
        except ValueError as e:
            return [types.TextContent(type="text", text=f"ERROR: {e}")]
        if not os.path.exists(directory):
            return [types.TextContent(type="text", text=f"Directory not found: {arguments['directory']}")]
        files = []
        for root, dirs, filenames in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', 'target', '__pycache__', '.venv']]
            for f in filenames:
                rel_path = os.path.relpath(os.path.join(root, f), PROJECT_ROOT)
                files.append(rel_path)
        return [types.TextContent(type="text", text="\n".join(files))]

    elif name == "run_maven_tests":
        result = subprocess.run(
            ["mvn", "test", "-q"],
            cwd=os.path.join(PROJECT_ROOT, "backend"),
            capture_output=True, text=True, timeout=120
        )
        output = result.stdout + result.stderr
        status = "PASSED" if result.returncode == 0 else "FAILED"
        return [types.TextContent(type="text", text=f"Maven Tests: {status}\n\n{output}")]

    elif name == "run_frontend_tests":
        result = subprocess.run(
            ["npm", "test", "--", "--watchAll=false", "--passWithNoTests"],
            cwd=os.path.join(PROJECT_ROOT, "frontend"),
            capture_output=True, text=True, timeout=120,
            env={**os.environ, "CI": "true"}
        )
        output = result.stdout + result.stderr
        status = "PASSED" if result.returncode == 0 else "FAILED"
        return [types.TextContent(type="text", text=f"Frontend Tests: {status}\n\n{output}")]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
