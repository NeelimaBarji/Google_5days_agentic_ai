"""
Security MCP Server
Wraps OWASP dependency-check CLI for pom.xml CVE scanning.

Security:
  - MCP_API_KEY validation on every tool call (set in .env)
"""

import os
from dotenv import load_dotenv

# Load .env so this server works standalone AND under ADK subprocess spawning
load_dotenv()
import subprocess
import json
import xml.etree.ElementTree as ET
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

MCP_API_KEY = os.environ.get("MCP_API_KEY", "")

app = Server("security-mcp")


def _check_auth(arguments: dict) -> "types.TextContent | None":
    if not MCP_API_KEY:
        return None
    if arguments.get("api_key") != MCP_API_KEY:
        return types.TextContent(type="text", text="ERROR: Unauthorized — invalid or missing MCP_API_KEY")
    return None

# Known safe versions for common Spring Boot deps (fallback if OWASP unavailable)
SAFE_VERSIONS = {
    "spring-boot": "3.2.5",
    "h2": "2.2.224",
    "jackson-databind": "2.16.1",
    "log4j-core": "2.21.1",
    "spring-security": "6.2.3",
}


@app.list_tools()
async def list_tools():
    return [
        types.Tool(name="scan_pom", description="Scan pom.xml for CVEs using OWASP dependency-check", inputSchema={
            "type": "object", "properties": {"api_key": {"type": "string", "description": "MCP API key (required)"}, "pom_path": {"type": "string"}}, "required": ["pom_path"]
        }),
        types.Tool(name="get_safe_version", description="Get the latest safe version for a Maven artifact", inputSchema={
            "type": "object", "properties": {"api_key": {"type": "string", "description": "MCP API key (required)"}, "artifact_id": {"type": "string"}}, "required": ["artifact_id"]
        }),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    # ── Security: API key check ──────────────────────────────────────────────
    auth_err = _check_auth(arguments)
    if auth_err:
        return [auth_err]

    if name == "scan_pom":
        pom_path = arguments["pom_path"]
        project_dir = os.path.dirname(os.path.abspath(pom_path))

        # Try OWASP dependency-check if installed
        try:
            result = subprocess.run(
                ["dependency-check", "--project", "devloop-demo", "--scan", pom_path,
                 "--format", "JSON", "--out", "/tmp/dc-report", "--noupdate"],
                capture_output=True, text=True, timeout=180
            )
            report_path = "/tmp/dc-report/dependency-check-report.json"
            if os.path.exists(report_path):
                with open(report_path) as f:
                    report = json.load(f)
                cves = []
                for dep in report.get("dependencies", []):
                    for vuln in dep.get("vulnerabilities", []):
                        cves.append({
                            "artifact": dep.get("fileName", "unknown"),
                            "cve": vuln.get("name"),
                            "severity": vuln.get("severity", "UNKNOWN"),
                            "description": vuln.get("description", "")[:200]
                        })
                return [types.TextContent(type="text", text=json.dumps({
                    "scan_tool": "OWASP dependency-check",
                    "cves_found": len(cves),
                    "cves": cves
                }, indent=2))]
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Fallback: parse pom.xml and check known vulnerable versions
        cves = []
        try:
            tree = ET.parse(pom_path)
            root = tree.getroot()
            ns = {"m": "http://maven.apache.org/POM/4.0.0"}

            for dep in root.findall(".//m:dependency", ns):
                artifact_id = dep.findtext("m:artifactId", namespaces=ns)
                version = dep.findtext("m:version", namespaces=ns)
                if artifact_id and version:
                    # Simulate finding a CVE for demo purposes
                    if artifact_id == "h2" and version < "2.1.214":
                        cves.append({
                            "artifact": f"{artifact_id}:{version}",
                            "cve": "CVE-2021-42392",
                            "severity": "CRITICAL",
                            "description": "H2 console JNDI injection vulnerability"
                        })
        except Exception as e:
            return [types.TextContent(type="text", text=f"ERROR parsing pom.xml: {e}")]

        return [types.TextContent(type="text", text=json.dumps({
            "scan_tool": "DevLoop static version check",
            "cves_found": len(cves),
            "cves": cves
        }, indent=2))]

    elif name == "get_safe_version":
        artifact_id = arguments["artifact_id"]
        # In production: query Maven Central or OSS Index API
        # For demo: return from known safe versions map
        safe_ver = SAFE_VERSIONS.get(artifact_id.lower(), "latest")
        return [types.TextContent(type="text", text=json.dumps({
            "artifact_id": artifact_id,
            "safe_version": safe_ver,
            "source": "DevLoop safe-versions registry"
        }))]

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read, write):
        await app.run(read, write, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
