# DevLoop — An Autonomous SDLC Agent That Ships Reviewed, Tested, Secure Code

**Subtitle:** Ten Google ADK agents and five MCP servers take a Jira ticket to an approved GitLab Merge Request in under 10 minutes.

**Track:** Agents for Business

---

## The Problem

In every software team, the distance between "the ticket is written" and "the code is merged" is enormous. A developer must read and interpret the ticket, explore the codebase, write the change, write unit tests, run integration checks, document the test evidence, open a merge request, wait for a reviewer, apply review feedback, re-run CI, and pass a security scan. For a routine change — a new field on an entity, a new API endpoint, a UI filter — this loop consumes hours to days of engineering time and reviewer attention, even though each individual step is well-defined and mechanical.

This is precisely the kind of problem where cost and revenue are on the line for a business: routine tickets clog sprint capacity, senior engineers spend review cycles on boilerplate, and delivery velocity drops. Industry estimates put routine, low-complexity changes at a substantial share of all tickets — automating them safely translates directly into recovered engineering capacity.

## Why Agents?

A single LLM call cannot solve this. The SDLC is a **stateful, multi-step workflow with hard dependencies**: code must exist before tests can be written, tests must pass before an MR should open, an MR must exist before it can be reviewed, and review comments must be addressed before approval. Each step needs different tools (filesystem, Maven, HTTP, GitLab API, CVE database) and different expertise (coding, testing, reviewing, security).

Agents map naturally onto this: each phase becomes a specialized agent with a focused prompt and a narrow toolset, and an orchestrating pipeline enforces the ordering. Agents can also **react** — when a test fails, the TestGeneratorAgent reads the failure output and repairs its own tests; when a reviewer flags issues, the FixAgent applies the fixes and re-pushes. That closed feedback loop is what makes this an agent problem rather than a code-generation problem.

## The Solution: DevLoop

DevLoop is a multi-agent system built on **Google ADK** that executes the complete software development lifecycle autonomously:

```
python devloop.py run PROD-1
```

One command. Ten agents. Roughly seven minutes later, a GitLab Merge Request exists — coded, unit-tested, integration-tested against the live running application, documented, peer-reviewed with inline comments, fixed, CVE-scanned, and approved.

DevLoop operates on **ProductFlow**, a realistic demo application included in the repo: a Spring Boot 3.2 (Java 21) REST backend with an H2 database and a React 18 frontend — the kind of stack found in thousands of enterprises.

## Architecture

```
CLI Input (ticket ID)
        │
        ▼
┌─────────────────────────────────────────────────────┐
│           Google ADK SequentialAgent Pipeline        │
│                                                      │
│  OrchestratorAgent → AnalysisAgent → DevAgent        │
│  → TestGeneratorAgent → IntegrationTestAgent         │
│  → TestDocAgent → MRAgent → ReviewAgent              │
│  → FixAgent → SecurityAgent                          │
└───────────┬──────────────────────┬───────────────────┘
            │ MCP (stdio)          │ MCP (stdio)
    ┌───────▼────────┐    ┌────────▼────────┐
    │  codebase-mcp  │    │   gitlab-mcp    │
    │  api-test-mcp  │    │  security-mcp   │
    │  jira-mcp      │    │                 │
    └────────────────┘    └─────────────────┘
            │
    ┌───────▼────────────────────┐
    │   Demo App (ProductFlow)   │
    │   Spring Boot :8080        │
    │   React UI   :3000         │
    └────────────────────────────┘
```

### The Ten Agents

| Agent | Responsibility |
|-------|----------------|
| **OrchestratorAgent** | Reads the Jira ticket, classifies BACKEND vs FRONTEND, builds pipeline context |
| **AnalysisAgent** | Scans the codebase and produces a precise change plan |
| **DevAgent** | Writes code changes across all affected files (reads before writing) |
| **TestGeneratorAgent** | Writes unit tests, runs them, self-heals on failure |
| **IntegrationTestAgent** | Calls the live API to verify the real running system |
| **TestDocAgent** | Generates a structured test evidence document |
| **MRAgent** | Creates the GitLab branch, pushes files, opens the Merge Request |
| **ReviewAgent** | Reviews the MR diff and posts actionable inline comments |
| **FixAgent** | Applies the review fixes, re-pushes, re-triggers CI |
| **SecurityAgent** | Scans pom.xml for CVEs, auto-remediates, approves the MR |

The pipeline uses ADK's `SequentialAgent` because each stage genuinely depends on the previous stage's output — sequential is the correct topology, not a simplification.

### Five Custom MCP Servers

All tool access goes through the **Model Context Protocol** over stdio, decoupling tool implementation from agent logic:

| Server | Tools |
|--------|-------|
| `codebase-mcp` | `read_file`, `write_file`, `list_files`, `run_maven_tests`, `run_frontend_tests` |
| `gitlab-mcp` | `create_branch`, `push_file`, `create_mr`, `get_mr_diff`, `post_mr_comment`, `approve_mr` |
| `api-test-mcp` | `http_get`, `http_post`, `http_put`, `verify_response` |
| `security-mcp` | `scan_pom`, `get_safe_version` |
| `jira-mcp` | `get_ticket`, `update_ticket_status` |

Each server is independently testable and replaceable. A `toolsets.py` factory hands each agent only the specific tools it needs — the ReviewAgent cannot write files; the DevAgent cannot approve MRs. This least-privilege tool assignment is both a design and a security decision.

## Security Features

Security is designed in, not bolted on:

1. **MCP API-key authentication.** Every tool call on all five MCP servers passes through `_check_auth()` before any logic runs. An invalid or missing `MCP_API_KEY` returns `ERROR: Unauthorized`.
2. **Path traversal prevention.** `codebase-mcp` routes every path through `safe_path()`, which resolves via `os.path.realpath()` and rejects anything escaping `PROJECT_ROOT` (e.g. `../../etc/passwd`).
3. **Automated CVE scanning and remediation.** The SecurityAgent runs OWASP dependency-check against `pom.xml` after every MR push and auto-remediates by bumping affected dependency versions.
4. **Credential hygiene.** All secrets live in a gitignored `.env`; `.env.example` documents the variables without values. The GitLab token stays inside `gitlab-mcp` — agents never see it.
5. **Least-privilege toolsets.** Agents receive only the tools their role requires.

## Deployability

The whole system is containerized: a `Dockerfile` for the agent and a `docker-compose.yml` that brings up backend, frontend, and agent together. A `.gitlab-ci.yml` defines a four-stage pipeline (build → test → security → notify) that re-runs on every commit DevLoop pushes — so the agent's own fix commits get real CI verification, visible in the MR's pipeline history.

## Demo: PROD-1, End to End

Ticket PROD-1: *"Add a `discount` field to the Product entity and expose it via the API."*

DevLoop, fully autonomously: classified the ticket as BACKEND with 6 affected files; modified `Product.java`, `ProductService.java`, a Flyway migration, and seed data; wrote 8 unit tests and ran them to green; called `GET /api/products/1` against the live server and verified the `discount` field in the JSON response; generated a test evidence document; created branch `feature/prod-1`, pushed 9 files, and opened the MR; posted 2 inline review comments on its own diff; applied both fixes and pushed a fix commit (re-triggering CI); ran the OWASP CVE scan (0 critical); and approved the MR.

**Total time: 7 minutes 01 seconds.** Two more demo tickets (a React status-filter dropdown and a low-stock endpoint) exercise the FRONTEND path and a second BACKEND path.

## Course Concepts Demonstrated

- **Multi-agent system with Google ADK** (code): ten `LlmAgent`s composed in a `SequentialAgent` pipeline, with `output_key` context passing between stages.
- **MCP servers** (code): five custom stdio MCP servers with typed tool schemas, consumed via ADK's `McpToolset`.
- **Security features** (code + video): API-key auth on every tool call, path-traversal guards, OWASP CVE scanning with auto-remediation, secret hygiene.
- **Deployability** (video): Dockerfile, docker-compose full-stack bring-up, and GitLab CI pipeline.
- **Agent skills / vibe coding workflow** (video): the project was built iteratively with AI-assisted coding as taught in the course.

## The Journey

The first version was a single mega-agent with all tools — it constantly confused phases, overwrote files it hadn't read, and opened MRs before tests passed. Splitting it into ten single-purpose agents with narrow toolsets fixed nearly all of it. The second hard lesson was code fidelity: LLMs love rewriting files from scratch. Enforcing a strict read-before-write discipline in the DevAgent's prompt preserved existing imports, annotations, and logic. Third, self-healing tests: piping Maven's failure output back to the TestGeneratorAgent turned flaky test generation into a reliable loop. Finally, making the ReviewAgent review a *diff* (not whole files) produced dramatically more precise, actionable comments — the same trick human reviewers use.

## Known Limitations

DevLoop performs best on additive changes (new fields, endpoints, UI filters); complex refactors need more sophisticated planning. It assumes a monorepo layout, doesn't yet handle merge conflicts if `main` advances mid-run, and Jira is mocked with local JSON (production would use Jira REST API v3).

## Links

- **Code repository (public, with full setup instructions):** https://gitlab.com/neelimabarji/devloop-demo
- **Live Merge Request produced by DevLoop:** https://gitlab.com/neelimabarji/devloop-demo/-/merge_requests/1
- **Video demo (5 min, YouTube):** [ADD YOUR YOUTUBE LINK]

---

*Built by Neelima Barji for the Kaggle × Google 5-Day AI Agents: Intensive Vibe Coding Capstone, 2026.*
