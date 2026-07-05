#!/usr/bin/env python3
"""
DevLoop CLI Entry Point
Usage: python devloop.py run PROD-1

Logging: every pipeline event is printed with a timestamp, the agent that
produced it, and what happened (thinking / tool call / tool result), so you
can always see exactly which agent is running and where execution is.
"""

import asyncio
import json
import sys
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

load_dotenv()

# Validate required env vars
for var in ["GITLAB_TOKEN", "GITLAB_PROJECT_ID", "GOOGLE_API_KEY"]:
    if not os.environ.get(var):
        print(f"❌ Missing environment variable: {var}")
        print("   Copy .env.example to .env and fill in your values.")
        sys.exit(1)

from agents.orchestrator import devloop_pipeline

# Seconds to wait between LLM turns (Free-Tier rate-limit protection).
# Override in .env, e.g. PACING_SECONDS=0 on a paid tier.
PACING_SECONDS = int(os.environ.get("PACING_SECONDS", "40"))

# Pipeline order — used to show progress as [step 3/10]
AGENT_ORDER = [
    ("OrchestratorAgent",     "Reading & classifying Jira ticket"),
    ("AnalysisAgent",         "Scanning codebase, planning changes"),
    ("DevAgent",              "Writing code changes"),
    ("TestGeneratorAgent",    "Writing & running unit tests"),
    ("IntegrationTestAgent",  "Verifying live API"),
    ("TestDocAgent",          "Generating test evidence doc"),
    ("MRAgent",               "Creating branch & Merge Request"),
    ("ReviewAgent",           "Reviewing MR diff"),
    ("FixAgent",              "Applying review fixes"),
    ("SecurityAgent",         "CVE scan & MR approval"),
]
AGENT_STEP = {name: i + 1 for i, (name, _) in enumerate(AGENT_ORDER)}
AGENT_ROLE = dict(AGENT_ORDER)


def ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def trunc(text: str, n: int = 300) -> str:
    text = " ".join(str(text).split())  # collapse whitespace for one-line logs
    return text if len(text) <= n else text[:n] + f"... [+{len(text) - n} chars]"


def fmt_args(args: dict) -> str:
    """Format tool-call args for logging: hide secrets, truncate long values."""
    shown = {}
    for k, v in (args or {}).items():
        if k == "api_key":
            shown[k] = "***"
        elif isinstance(v, str) and len(v) > 80:
            shown[k] = v[:80] + f"...[+{len(v) - 80}]"
        else:
            shown[k] = v
    return json.dumps(shown, ensure_ascii=False)


def agent_banner(name: str, start_time: float):
    step = AGENT_STEP.get(name)
    role = AGENT_ROLE.get(name, "")
    elapsed = int(time.time() - start_time)
    label = f"STEP {step}/{len(AGENT_ORDER)}" if step else "AGENT"
    print("\n" + "─" * 62)
    print(f"▶ [{ts()}] {label}: {name} — {role}  (elapsed {elapsed // 60}m{elapsed % 60:02d}s)")
    print("─" * 62)


async def run_pipeline(ticket_id: str):
    start_time = time.time()
    print(f"\n🚀 [{ts()}] DevLoop starting for ticket: {ticket_id}")
    print(f"   Pipeline: {' → '.join(n for n, _ in AGENT_ORDER)}")
    print(f"   Pacing between LLM turns: {PACING_SECONDS}s (set PACING_SECONDS in .env to change)")
    print("=" * 62)

    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="devloop",
        user_id="devloop-agent",
        session_id=f"session-{ticket_id}",
    )

    runner = Runner(
        agent=devloop_pipeline,
        app_name="devloop",
        session_service=session_service,
    )

    message = genai_types.Content(
        role="user",
        parts=[genai_types.Part(text=f"Process Jira ticket: {ticket_id}")],
    )

    current_agent = None
    last_final_text = None

    async for event in runner.run_async(
        user_id="devloop-agent",
        session_id=f"session-{ticket_id}",
        new_message=message,
    ):
        author = getattr(event, "author", None)
        llm_turn = False  # did this event consume an LLM request? (drives pacing)

        # ── New agent taking over → print a step banner ──────────────────
        if author and author != current_agent and author != "user":
            current_agent = author
            agent_banner(author, start_time)

        # ── Log every part of the event: text / tool calls / tool results ─
        if event.content and event.content.parts:
            for part in event.content.parts:
                # Agent's reasoning / output text
                if getattr(part, "text", None):
                    print(f"  💬 [{ts()}] [{author}] {trunc(part.text)}")
                    llm_turn = True

                # Agent decided to call a tool
                fc = getattr(part, "function_call", None)
                if fc:
                    print(f"  🔧 [{ts()}] [{author}] TOOL CALL → {fc.name}({fmt_args(dict(fc.args or {}))})")
                    llm_turn = True

                # Tool returned a result
                fr = getattr(part, "function_response", None)
                if fr:
                    resp = fr.response
                    if isinstance(resp, dict):
                        resp = resp.get("result", resp)
                    result_text = trunc(resp, 200)
                    marker = "❌" if "ERROR" in str(resp) else "✅"
                    print(f"  {marker} [{ts()}] [{author}] TOOL RESULT ← {fr.name}: {result_text}")

        # ── Remember the latest final response (a SequentialAgent emits one
        #    per sub-agent — the pipeline is only done when the stream ends,
        #    so we must NOT break out of this loop early) ───────────────────
        if event.is_final_response():
            if event.content and event.content.parts and event.content.parts[0].text:
                last_final_text = event.content.parts[0].text

        # ── Free-Tier pacing: only after events that used an LLM request ──
        if llm_turn and PACING_SECONDS > 0:
            print(f"  ⏸  [{ts()}] Pacing {PACING_SECONDS}s (Free-Tier rate-limit protection)...")
            await asyncio.sleep(PACING_SECONDS)

    # Stream ended → the whole pipeline is complete
    total = int(time.time() - start_time)
    print("\n" + "=" * 62)
    print(f"✅ [{ts()}] DevLoop Pipeline Complete!  Total time: {total // 60}m{total % 60:02d}s")
    print("=" * 62)
    if last_final_text:
        print(last_final_text)


class Tee:
    """Mirror stdout to a log file so every run is saved automatically."""

    def __init__(self, path):
        self.terminal = sys.stdout
        self.log = open(path, "w", encoding="utf-8")

    def write(self, msg):
        self.terminal.write(msg)
        self.log.write(msg)
        self.log.flush()  # survive Ctrl-C / crashes

    def flush(self):
        self.terminal.flush()
        self.log.flush()


def main():
    if len(sys.argv) < 3 or sys.argv[1] != "run":
        print("Usage: python devloop.py run <TICKET_ID>")
        print("Example: python devloop.py run PROD-1")
        sys.exit(1)

    ticket_id = sys.argv[2].upper()

    # Save the full terminal output of every run to logs/
    os.makedirs("logs", exist_ok=True)
    log_path = f"logs/devloop-{ticket_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    sys.stdout = Tee(log_path)
    print(f"📝 Saving run log to: {log_path}")

    try:
        asyncio.run(run_pipeline(ticket_id))
    finally:
        print(f"\n📝 Full run log saved: {log_path}")


if __name__ == "__main__":
    main()
