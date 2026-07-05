"""
Shared configuration for DevLoop agents.

Centralizes the Gemini model name so it can be changed in one place
(via the GEMINI_MODEL environment variable) instead of being hardcoded
in every agent file.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Gemini model used by all DevLoop agents.
# Override by setting GEMINI_MODEL in your .env file (see .env.example).
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")


# ── MCP tool-call security ────────────────────────────────────────────────
# Every MCP server validates an api_key argument on every tool call.
# This instruction is appended to every agent's prompt so the LLM always
# includes the key. (The GitLab token itself never reaches any agent.)
MCP_API_KEY = os.environ.get("MCP_API_KEY", "")
MCP_SECURITY_INSTRUCTION = (
    f'\n\nSECURITY REQUIREMENT (MANDATORY): Every single tool call you make MUST '
    f'include the argument api_key="{MCP_API_KEY}". Tool calls without it will be '
    f'rejected with ERROR: Unauthorized. Never omit it, never alter it.'
) if MCP_API_KEY else ""
