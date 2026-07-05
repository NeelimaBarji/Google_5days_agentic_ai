"""
GitLab MCP Server
Exposes GitLab API operations: branch management, file push, MR creation, review comments.

Security:
  - MCP_API_KEY validation on every tool call (set in .env)
  - GITLAB_TOKEN never exposed to agents — used only inside this server
"""

import os
from dotenv import load_dotenv

# Load .env so this server works standalone AND under ADK subprocess spawning
load_dotenv()
import base64
import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

GITLAB_URL = os.environ.get("GITLAB_URL", "https://gitlab.com")
GITLAB_TOKEN = os.environ.get("GITLAB_TOKEN", "")  # Set in .env — never passed to agents
GITLAB_PROJECT_ID = os.environ.get("GITLAB_PROJECT_ID", "")  # Set in .env
MCP_API_KEY = os.environ.get("MCP_API_KEY", "")

app = Server("gitlab-mcp")
headers = {"PRIVATE-TOKEN": GITLAB_TOKEN, "Content-Type": "application/json"}


def _check_auth(arguments: dict) -> "types.TextContent | None":
    if not MCP_API_KEY:
        return None
    if arguments.get("api_key") != MCP_API_KEY:
        return types.TextContent(type="text", text="ERROR: Unauthorized — invalid or missing MCP_API_KEY")
    return None


def api(path: str) -> str:
    return f"{GITLAB_URL}/api/v4/projects/{GITLAB_PROJECT_ID}{path}"


@app.list_tools()
async def list_tools():
    return [
        types.Tool(name="create_branch", description="Create a new GitLab branch", inputSchema={
            "type": "object",
            "properties": {"api_key": {"type": "string", "description": "MCP API key (required)"}, "branch_name": {"type": "string"}, "ref": {"type": "string", "default": "master"}},
            "required": ["branch_name"]
        }),
        types.Tool(name="push_file", description="Push a file to a GitLab branch", inputSchema={
            "type": "object",
            "properties": {"api_key": {"type": "string", "description": "MCP API key (required)"}, 
                "branch": {"type": "string"}, "path": {"type": "string"},
                "content": {"type": "string"}, "commit_message": {"type": "string"}
            },
            "required": ["branch", "path", "content", "commit_message"]
        }),
        types.Tool(name="create_mr", description="Create a GitLab Merge Request", inputSchema={
            "type": "object",
            "properties": {"api_key": {"type": "string", "description": "MCP API key (required)"}, 
                "branch": {"type": "string"}, "title": {"type": "string"},
                "description": {"type": "string"}, "target_branch": {"type": "string", "default": "main"}
            },
            "required": ["branch", "title", "description"]
        }),
        types.Tool(name="get_mr_diff", description="Get the diff for a Merge Request", inputSchema={
            "type": "object", "properties": {"api_key": {"type": "string", "description": "MCP API key (required)"}, "mr_id": {"type": "integer"}}, "required": ["mr_id"]
        }),
        types.Tool(name="post_mr_comment", description="Post a comment on a Merge Request", inputSchema={
            "type": "object",
            "properties": {"api_key": {"type": "string", "description": "MCP API key (required)"}, "mr_id": {"type": "integer"}, "comment": {"type": "string"}},
            "required": ["mr_id", "comment"]
        }),
        types.Tool(name="approve_mr", description="Approve a Merge Request", inputSchema={
            "type": "object", "properties": {"api_key": {"type": "string", "description": "MCP API key (required)"}, "mr_id": {"type": "integer"}}, "required": ["mr_id"]
        }),
        types.Tool(name="get_pipeline_status", description="Get CI pipeline status", inputSchema={
            "type": "object", "properties": {"api_key": {"type": "string", "description": "MCP API key (required)"}, "pipeline_id": {"type": "integer"}}, "required": ["pipeline_id"]
        }),
        types.Tool(name="merge_mr", description="Merge an approved Merge Request into the target branch", inputSchema={
            "type": "object",
            "properties": {"api_key": {"type": "string", "description": "MCP API key (required)"}, 
                "mr_id": {"type": "integer"},
                "merge_commit_message": {"type": "string", "description": "Optional merge commit message"}
            },
            "required": ["mr_id"]
        }),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    # ── Security: API key check ──────────────────────────────────────────────
    auth_err = _check_auth(arguments)
    if auth_err:
        return [auth_err]

    async with httpx.AsyncClient() as client:

        if name == "create_branch":
            r = await client.post(api("/repository/branches"), headers=headers, json={
                "branch": arguments["branch_name"],
                "ref": arguments.get("ref", "master")
            })
            if r.status_code in (200, 201):
                return [types.TextContent(type="text", text=f"Branch created: {arguments['branch_name']}")]
            return [types.TextContent(type="text", text=f"ERROR: {r.status_code} {r.text}")]

        elif name == "push_file":
            encoded = base64.b64encode(arguments["content"].encode()).decode()
            # Try update first, then create
            r = await client.put(api(f"/repository/files/{arguments['path'].replace('/', '%2F')}"),
                headers=headers, json={
                    "branch": arguments["branch"],
                    "content": arguments["content"],
                    "commit_message": arguments["commit_message"],
                    "encoding": "text"
                })
            if r.status_code == 400:
                r = await client.post(api(f"/repository/files/{arguments['path'].replace('/', '%2F')}"),
                    headers=headers, json={
                        "branch": arguments["branch"],
                        "content": arguments["content"],
                        "commit_message": arguments["commit_message"],
                        "encoding": "text"
                    })
            status = "pushed" if r.status_code in (200, 201) else f"FAILED ({r.status_code})"
            return [types.TextContent(type="text", text=f"File {arguments['path']}: {status}")]

        elif name == "create_mr":
            r = await client.post(api("/merge_requests"), headers=headers, json={
                "source_branch": arguments["branch"],
                "target_branch": arguments.get("target_branch", "master"),
                "title": arguments["title"],
                "description": arguments["description"],
            })
            data = r.json()
            return [types.TextContent(type="text", text=f"MR created: {data.get('web_url')} (ID: {data.get('iid')})")]

        elif name == "get_mr_diff":
            r = await client.get(api(f"/merge_requests/{arguments['mr_id']}/diffs"), headers=headers)
            diffs = r.json()
            summary = "\n\n".join([
                f"--- {d['old_path']}\n+++ {d['new_path']}\n{d.get('diff', '')[:2000]}"
                for d in diffs[:5]
            ])
            return [types.TextContent(type="text", text=summary)]

        elif name == "post_mr_comment":
            r = await client.post(api(f"/merge_requests/{arguments['mr_id']}/notes"),
                headers=headers, json={"body": arguments["comment"]})
            return [types.TextContent(type="text", text=f"Comment posted: {r.status_code}")]

        elif name == "approve_mr":
            r = await client.post(api(f"/merge_requests/{arguments['mr_id']}/approve"), headers=headers)
            return [types.TextContent(type="text", text=f"MR approved: {r.status_code}")]

        elif name == "get_pipeline_status":
            r = await client.get(api(f"/pipelines/{arguments['pipeline_id']}"), headers=headers)
            data = r.json()
            return [types.TextContent(type="text", text=f"Pipeline {arguments['pipeline_id']}: {data.get('status')}")]

        elif name == "merge_mr":
            payload = {"should_remove_source_branch": False}
            if arguments.get("merge_commit_message"):
                payload["merge_commit_message"] = arguments["merge_commit_message"]
            r = await client.put(
                api(f"/merge_requests/{arguments['mr_id']}/merge"),
                headers=headers,
                json=payload
            )
            if r.status_code == 200:
                data = r.json()
                return [types.TextContent(type="text", text=f"✅ MR !{arguments['mr_id']} merged into {data.get('target_branch')}")]
            return [types.TextContent(type="text", text=f"ERROR merging MR: {r.status_code} {r.text}")]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
