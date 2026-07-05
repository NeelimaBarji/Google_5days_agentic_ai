#!/usr/bin/env python3
"""
Run a SINGLE DevLoop agent standalone (without the full 10-agent pipeline).
Useful for testing one stage — e.g. MRAgent — in isolation.

Usage:
    python run_agent.py mr                    # MRAgent with built-in PROD-2 test context
    python run_agent.py review               # ReviewAgent (pass MR id in the message)
    python run_agent.py mr "custom context message..."

Agents get their context from the pipeline session state normally; when run
standalone, we pass that context in the user message instead.
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types


def ts():
    return datetime.now().strftime("%H:%M:%S")


# ── Agent registry: name → (import path, attribute, default test message) ──
AGENTS = {
    "orchestrator": ("agents.orchestrator", "orchestrator_agent",
                     "Process Jira ticket: PROD-2"),
    "analysis":     ("agents.analysis_agent", "analysis_agent",
                     "Ticket PROD-2 (FRONTEND): Show total product count above the product list. Affected: frontend/src/components/ProductList.jsx"),
    "dev":          ("agents.dev_agent", "dev_agent",
                     "Ticket PROD-2 (FRONTEND): Show total product count above the product list, e.g. 'Showing 7 products' (singular when 1). Modify frontend/src/components/ProductList.jsx only."),
    "testgen":      ("agents.test_generator_agent", "test_generator_agent",
                     "Ticket PROD-2: product count label was added to frontend/src/components/ProductList.jsx. Write and run frontend tests."),
    "mr":           ("agents.mr_agent", "mr_agent", json.dumps({
                        "pipeline_context": {
                            "ticket_id": "PROD-2",
                            "title": "Show total product count above the product list",
                            "branch_name": "feature/prod-2",
                            "acceptance_criteria": [
                                "Label 'Showing N products' appears above the list",
                                "Singular form for 1 product",
                            ],
                        },
                        "dev_output": {"modified_files": ["frontend/src/components/ProductList.jsx"]},
                        "test_results": "Frontend tests: passed",
                        "instruction": "Create branch feature/prod-2 from master, push the modified files listed above (read each with read_file first), and open the Merge Request targeting master. There is no test report file for this ticket — skip pushing a report.",
                     })),
    "review":       ("agents.review_agent", "review_agent",
                     "Review Merge Request with mr_id=2 for ticket PROD-2 (product count label in ProductList.jsx). Fetch the diff and post inline review comments."),
    "fix":          ("agents.fix_agent", "fix_agent",
                     "Apply review fixes for MR mr_id=2, branch feature/prod-2."),
    "security":     ("agents.security_agent", "security_agent",
                     "Run security scan on backend/pom.xml and approve MR mr_id=2 if clean."),
}


async def run_single(agent_key: str, message_text: str):
    import importlib
    module_path, attr, _ = AGENTS[agent_key]
    agent = getattr(importlib.import_module(module_path), attr)

    print(f"\n🔬 [{ts()}] Running SINGLE agent: {agent.name}")
    print(f"   Context message: {message_text[:200]}{'...' if len(message_text) > 200 else ''}")
    print("=" * 62)

    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="devloop-single", user_id="dev", session_id="single")
    runner = Runner(agent=agent, app_name="devloop-single",
                    session_service=session_service)

    message = genai_types.Content(role="user",
                                  parts=[genai_types.Part(text=message_text)])
    start = time.time()

    async for event in runner.run_async(user_id="dev", session_id="single",
                                        new_message=message):
        if not (event.content and event.content.parts):
            continue
        for part in event.content.parts:
            if getattr(part, "text", None):
                print(f"  💬 [{ts()}] {part.text.strip()[:400]}")
            fc = getattr(part, "function_call", None)
            if fc:
                args = {k: ("***" if k == "api_key" else v) for k, v in dict(fc.args or {}).items()}
                print(f"  🔧 [{ts()}] TOOL CALL → {fc.name}({json.dumps(args)[:250]})")
            fr = getattr(part, "function_response", None)
            if fr:
                resp = fr.response.get("result", fr.response) if isinstance(fr.response, dict) else fr.response
                marker = "❌" if "ERROR" in str(resp) else "✅"
                print(f"  {marker} [{ts()}] TOOL RESULT ← {fr.name}: {str(resp)[:250]}")

    total = int(time.time() - start)
    print("=" * 62)
    print(f"✅ [{ts()}] {agent.name} finished in {total // 60}m{total % 60:02d}s\n")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in AGENTS:
        print("Usage: python run_agent.py <agent> [\"custom context message\"]")
        print(f"Agents: {', '.join(AGENTS)}")
        sys.exit(1)
    key = sys.argv[1]
    message = sys.argv[2] if len(sys.argv) > 2 else AGENTS[key][2]
    asyncio.run(run_single(key, message))


if __name__ == "__main__":
    main()
