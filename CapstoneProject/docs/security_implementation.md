# Agent Security Implementation

Agent security is implemented in the DevLoop codebase in two distinct ways: through a dedicated security-focused agent, and through security measures enforced by the MCP servers that host the agent tools.

## 1. The Security Agent (`agents/security_agent.py`)

A dedicated `SecurityAgent` is implemented using Google ADK to run independently in the pipeline. It handles security vulnerabilities in the following manner:

- **Automated Scanning:** Scans the backend's `pom.xml` for CVEs using OWASP dependency-check (`scan_pom` tool).
- **Vulnerability Remediation:** If vulnerabilities are found, it fetches patched, safe versions (`get_safe_version` tool).
- **Automated Fixes:** Modifies `pom.xml` with the fixed dependencies, and pushes the fix back to the repository.
- **Reporting:** Posts a formatted security comment on the corresponding Merge Request detailing the CVEs and the applied fixes.

## 2. MCP Server Security (`mcp_servers/codebase_mcp.py` & `mcp_servers/security_mcp.py`)

The Model Context Protocol (MCP) servers, which expose tools to the agents, have built-in security features to prevent agents from inadvertently or maliciously causing harm to the host environment:

- **API Key Authentication:** Every tool call on the MCP servers verifies an `MCP_API_KEY` via an internal `_check_auth` function. This ensures that only authorized agents can execute tools, returning an `ERROR: Unauthorized` message if the key is missing or invalid.
- **Path Traversal Prevention:** The `codebase_mcp.py` server implements a `safe_path()` function. This specifically protects against path traversal vulnerabilities (e.g., trying to read `../../etc/passwd`). It resolves all requested file paths relative to `PROJECT_ROOT` and verifies that the resulting path does not escape the project's root directory, returning a `ValueError` if an escape attempt is detected.
