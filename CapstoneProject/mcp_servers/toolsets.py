"""
MCP Toolsets Factory for ADK Agents
Provides McpToolset instances connected via stdio to local MCP servers.
"""

import os
import sys
from typing import List, Optional
from dotenv import load_dotenv
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

# Ensure .env is loaded before we snapshot the environment for subprocesses
load_dotenv()

MCP_SERVERS_DIR = os.path.abspath(os.path.dirname(__file__))


def _get_mcp_toolset(script_name: str, tool_filter: Optional[List[str]] = None) -> McpToolset:
    script_path = os.path.join(MCP_SERVERS_DIR, script_name)
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=[script_path],
                # CRITICAL: MCP spawns servers with a minimal environment by
                # default — GITLAB_TOKEN etc. would NOT be inherited. Pass the
                # full parent environment (which includes .env values).
                env=dict(os.environ),
            ),
            # Default is 5s — far too short for long-running tools like
            # run_maven_tests, OWASP scans, and GitLab pushes.
            timeout=300,
        ),
        tool_filter=tool_filter,
    )


def get_codebase_toolset(tool_filter: Optional[List[str]] = None) -> McpToolset:
    return _get_mcp_toolset("codebase_mcp.py", tool_filter)


def get_gitlab_toolset(tool_filter: Optional[List[str]] = None) -> McpToolset:
    return _get_mcp_toolset("gitlab_mcp.py", tool_filter)


def get_api_test_toolset(tool_filter: Optional[List[str]] = None) -> McpToolset:
    return _get_mcp_toolset("api_test_mcp.py", tool_filter)


def get_security_toolset(tool_filter: Optional[List[str]] = None) -> McpToolset:
    return _get_mcp_toolset("security_mcp.py", tool_filter)


def get_jira_toolset(tool_filter: Optional[List[str]] = None) -> McpToolset:
    return _get_mcp_toolset("jira_mcp.py", tool_filter)
