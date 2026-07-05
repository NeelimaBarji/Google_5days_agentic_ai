"""
Pre-flight check: verifies the GitLab MCP server works end-to-end
BEFORE running a full DevLoop pipeline.

Tests, in order:
  1. .env variables are present
  2. GITLAB_TOKEN + GITLAB_PROJECT_ID are valid (direct API call)
  3. gitlab_mcp.py spawns over stdio (same as ADK does) and lists tools
  4. create_branch works through MCP (creates + then deletes a throwaway branch)

Run:  python verify_gitlab_mcp.py
"""

import asyncio
import os
import sys

import httpx
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

GITLAB_URL = os.environ.get("GITLAB_URL", "https://gitlab.com")
TOKEN = os.environ.get("GITLAB_TOKEN", "")
PROJECT_ID = os.environ.get("GITLAB_PROJECT_ID", "")
MCP_API_KEY = os.environ.get("MCP_API_KEY", "")
TEST_BRANCH = "mcp-verify-test"

HEADERS = {"PRIVATE-TOKEN": TOKEN}


def ok(msg):   print(f"  ✅ {msg}")
def fail(msg): print(f"  ❌ {msg}"); sys.exit(1)


def step1_env():
    print("\n[1/4] Checking .env variables...")
    for var in ("GITLAB_TOKEN", "GITLAB_PROJECT_ID", "MCP_API_KEY"):
        if not os.environ.get(var):
            fail(f"{var} is missing — check your .env file")
    ok("GITLAB_TOKEN, GITLAB_PROJECT_ID, MCP_API_KEY all set")


def step2_direct_api():
    print("\n[2/4] Verifying token + project ID against GitLab API...")
    r = httpx.get(f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}", headers=HEADERS)
    if r.status_code == 401:
        fail("401 Unauthorized — token is invalid/revoked. Create a new one with 'api' scope.")
    if r.status_code == 404:
        fail(f"404 — project ID {PROJECT_ID} not found (or token lacks access).")
    if r.status_code != 200:
        fail(f"Unexpected {r.status_code}: {r.text[:200]}")
    data = r.json()
    ok(f"Token valid. Project: {data['path_with_namespace']} (default branch: {data['default_branch']})")
    return data["default_branch"]


async def step3_and_4_mcp(default_branch: str):
    print("\n[3/4] Spawning gitlab_mcp.py over stdio (exactly how ADK does)...")
    server = StdioServerParameters(
        command=sys.executable,
        args=[os.path.join(os.path.dirname(__file__), "mcp_servers", "gitlab_mcp.py")],
        env=dict(os.environ),  # same env-passing fix as toolsets.py
    )
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = [t.name for t in tools.tools]
            if "create_branch" not in names:
                fail(f"create_branch not in tool list: {names}")
            ok(f"MCP server up. {len(names)} tools: {', '.join(names)}")

            print(f"\n[4/4] Creating throwaway branch '{TEST_BRANCH}' via MCP...")
            result = await session.call_tool("create_branch", {
                "branch_name": TEST_BRANCH,
                "ref": default_branch,
                "api_key": MCP_API_KEY,
            })
            text = result.content[0].text
            if "ERROR" in text:
                fail(f"create_branch failed: {text}")
            ok(text)

    # Cleanup: delete the test branch via direct API
    r = httpx.delete(
        f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}/repository/branches/{TEST_BRANCH}",
        headers=HEADERS,
    )
    if r.status_code == 204:
        ok(f"Cleanup: '{TEST_BRANCH}' deleted")
    else:
        print(f"  ⚠️ Cleanup returned {r.status_code} — delete '{TEST_BRANCH}' manually on GitLab")


if __name__ == "__main__":
    step1_env()
    default_branch = step2_direct_api()
    asyncio.run(step3_and_4_mcp(default_branch))
    print("\n🎉 All checks passed — GitLab MCP is working. Safe to run: python devloop.py run PROD-2\n")
