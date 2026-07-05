# DevLoop — Autonomous SDLC Agent for Java Spring Boot

> **Google 5-Day AI Agents: Intensive Vibe Coding Capstone | Agents for Business Track**
> **Author:** Neelima Barji

DevLoop is a **multi-agent AI system** that autonomously executes the complete software development lifecycle — from reading a Jira ticket to merging tested, secure code on GitLab — in under 10 minutes.

```
python devloop.py run PROD-1
```

One command. Ten agents. A fully reviewed, tested, and approved Merge Request.

---

## The Problem

In every software team, the distance between "ticket written" and "code merged" is enormous. For even a routine change — a new entity field, a new endpoint, a UI filter — a developer must interpret the ticket, explore the codebase, write the change, write and run unit tests, verify against the running system, document test evidence, open a merge request, wait for review, apply feedback, re-run CI, and pass a security scan. Hours to days of engineering and reviewer time are consumed by steps that are well-defined and mechanical. Routine tickets clog sprint capacity and senior engineers burn review cycles on boilerplate — a direct cost to the business.

## The Solution — and Why Agents?

DevLoop automates this entire loop. A single LLM call can't: the SDLC is a **stateful, multi-step workflow with hard dependencies** (code before tests, passing tests before an MR, an MR before review, fixes before approval), where each step needs different tools (filesystem, Maven, HTTP, GitLab API, CVE database) and different expertise. Agents map naturally onto this — each phase is a specialized agent with a focused prompt and a least-privilege toolset, orchestrated in a strict pipeline. Agents also **react**: failing tests are self-healed from Maven output, and review comments are applied automatically before re-triggering CI.

---

## Architecture

```
CLI Input (ticket ID)
        │
        ▼
┌─────────────────────────────────────────────────────┐
│              Google ADK SequentialAgent Pipeline    │
│                                                     │
│  OrchestratorAgent → AnalysisAgent → DevAgent      │
│  → TestGeneratorAgent → IntegrationTestAgent        │
│  → TestDocAgent → MRAgent → ReviewAgent            │
│  → FixAgent → SecurityAgent                        │
└───────────┬──────────────────────┬──────────────────┘
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

**10 Specialized Agents:**

| Agent | Role |
|-------|------|
| OrchestratorAgent | Reads Jira ticket, classifies BACKEND vs FRONTEND |
| AnalysisAgent | Scans codebase, produces precise change plan |
| DevAgent | Writes code changes across all affected files |
| TestGeneratorAgent | Writes unit tests, runs them, self-heals on failure |
| IntegrationTestAgent | Calls the live API to verify the real running system |
| TestDocAgent | Generates structured test evidence document |
| MRAgent | Creates GitLab branch, pushes files, opens Merge Request |
| ReviewAgent | Reviews the MR diff, posts actionable inline comments |
| FixAgent | Applies review fixes, re-pushes, triggers CI again |
| SecurityAgent | Scans pom.xml for CVEs, auto-remediates, approves MR |

**5 MCP Servers:**

| Server | Tools |
|--------|-------|
| `codebase-mcp` | `read_file`, `write_file`, `list_files`, `run_maven_tests`, `run_frontend_tests` |
| `gitlab-mcp` | `create_branch`, `push_file`, `create_mr`, `get_mr_diff`, `post_mr_comment`, `approve_mr` |
| `api-test-mcp` | `http_get`, `http_post`, `http_put`, `verify_response` |
| `security-mcp` | `scan_pom`, `get_safe_version` |
| `jira-mcp` | `get_ticket`, `update_ticket_status` |

---

## Demo: PROD-1 End-to-End Run

PROD-1 ticket: *"Add a `discount` field to the Product entity and expose it via the API."*

**What DevLoop did automatically:**
1. Read and classified the ticket (BACKEND, 6 files to change)
2. Wrote code: `Product.java`, `ProductService.java`, `V1__add_discount.sql`, `data.sql`
3. Wrote 8 unit tests, ran them — all passed
4. Called `GET /api/products/1` live — verified `discount` field in response
5. Generated test evidence document
6. Created branch `feature/prod-1`, pushed 9 files, opened MR
7. Posted 2 inline review comments on the diff
8. Applied both fixes, pushed fix commit (CI pipeline re-triggered)
9. Ran OWASP CVE scan — 0 critical issues
10. Approved the MR

**Total time: 7 minutes 01 seconds**

Live MR: https://gitlab.com/neelimabarji/devloop-demo/-/merge_requests/1

---

## Demo Application: ProductFlow

The target codebase DevLoop modifies — a realistic Spring Boot + React product management system.

**Backend** (Spring Boot 3.2, Java 21, H2):
```
GET    /api/products              List all products (optional ?status= filter)
GET    /api/products/{id}         Get single product
POST   /api/products              Create product
PUT    /api/products/{id}         Update product
DELETE /api/products/{id}         Delete product
GET    /api/products/low-stock    Products with stock < threshold
```

**Frontend** (React 18, Vite):
- Product list with search, category filter tabs, status badges
- Low-stock warning icons
- Create / edit / detail forms

---

## Demo Tickets

| Ticket | Type | Description |
|--------|------|-------------|
| PROD-1 | BACKEND | Add `discount` field to Product (decimal 0.0–1.0) |
| PROD-2 | FRONTEND | Show total product count above the product list |
| PROD-3 | BACKEND | Add `GET /api/products/low-stock` endpoint |

---

## Project Structure

```
devloop/
├── devloop.py                    ← CLI entry point
├── requirements.txt
├── .env.example
├── .gitlab-ci.yml                ← CI: build → test → security → notify
├── docker-compose.yml            ← Full stack: backend + frontend + agent
├── Dockerfile                    ← Agent container
│
├── agents/
│   ├── orchestrator.py           ← SequentialAgent pipeline
│   ├── analysis_agent.py
│   ├── dev_agent.py
│   ├── test_generator_agent.py
│   ├── integration_test_agent.py
│   ├── test_doc_agent.py
│   ├── mr_agent.py
│   ├── review_agent.py
│   ├── fix_agent.py
│   └── security_agent.py
│
├── mcp_servers/
│   ├── codebase_mcp.py
│   ├── gitlab_mcp.py
│   ├── api_test_mcp.py
│   ├── security_mcp.py
│   ├── jira_mcp.py
│   └── toolsets.py               ← McpToolset factory functions
│
├── jira-tickets/
│   ├── PROD-1.json
│   ├── PROD-2.json
│   └── PROD-3.json
│
├── docs/
│   ├── CapstoneProject.md        ← Full architecture & design doc
│   ├── prod-1-run.md             ← PROD-1 execution log
│   └── PROD-1-test-report.md     ← Generated test evidence
│
├── backend/                      ← Spring Boot (Java 21)
│   ├── pom.xml
│   └── src/
│
└── frontend/                     ← React 18 + Vite
    ├── package.json
    └── src/
```

---

## Setup & Running

### Prerequisites

- Python 3.11+
- Java 21+ and Maven 3.9+
- Node.js 20+
- GitLab account (free tier works) with a project
- Google AI Studio API key — [aistudio.google.com](https://aistudio.google.com)

### 1. Clone & configure

```bash
git clone https://gitlab.com/neelimabarji/devloop-demo.git
cd devloop-demo
cp .env.example .env
```

Edit `.env`:

```env
GOOGLE_API_KEY=<from aistudio.google.com>
GITLAB_TOKEN=<GitLab Personal Access Token with api scope>
GITLAB_PROJECT_ID=<numeric project ID from GitLab Settings → General>
PROJECT_ROOT=/absolute/path/to/devloop
MCP_API_KEY=<any random secret string, e.g. devloop-secret-123>
```

### 2. Install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Start the demo application

```bash
# Terminal 1 — Spring Boot backend
cd backend && mvn spring-boot:run
# Starts at http://localhost:8080

# Terminal 2 — React frontend
cd frontend && npm install && npm start
# Opens at http://localhost:3000
```

### 4. Verify the app is running

```bash
curl http://localhost:8080/api/products
# Returns JSON array of 7 seeded products
```

### 5. Run DevLoop

```bash
# Terminal 3
python devloop.py run PROD-1

# Run all three demo scenarios:
python devloop.py run PROD-1   # Backend: add discount field
python devloop.py run PROD-2   # Frontend: show product count label
python devloop.py run PROD-3   # Backend: low-stock endpoint
```

Watch the agent-by-agent output. In ~7–10 minutes a GitLab MR will be created, reviewed, fixed, and approved automatically.

---

## Running with Docker Compose

```bash
# Fill in .env first, then:
docker compose up --build

# All three services start automatically.
# DevLoop agent runs PROD-1 on startup.
```

---

## Security Features

**1. MCP API Key validation** — All five MCP servers call `_check_auth(arguments)` as the first line of every tool invocation. The `MCP_API_KEY` is passed as an `api_key` argument alongside every tool call. Missing or incorrect keys return `ERROR: Unauthorized` — no tool logic runs.

```python
def _check_auth(arguments: dict):
    if arguments.get("api_key") != MCP_API_KEY:
        return types.TextContent(type="text", text="ERROR: Unauthorized — invalid or missing MCP_API_KEY")
```

**2. Path traversal prevention** — `codebase-mcp` routes every file path through `safe_path()` before any read or write. Uses `os.path.realpath()` to fully resolve the path, then asserts it stays inside `PROJECT_ROOT`. Traversal attempts (e.g. `../../etc/passwd`) raise `ValueError` and return an error without touching the filesystem.

```python
def safe_path(base: str, requested: str) -> str:
    resolved = os.path.realpath(os.path.join(base, requested))
    if not resolved.startswith(os.path.realpath(base)):
        raise ValueError(f"Path traversal detected: '{requested}' escapes project root")
    return resolved
```

**3. OWASP CVE scanning** — `SecurityAgent` runs `dependency-check` against `pom.xml` after every MR push. CVEs are auto-remediated by updating the affected dependency version directly in `pom.xml`, then pushing a fix commit.

**4. Credential hygiene** — All secrets (`GITLAB_TOKEN`, `GOOGLE_API_KEY`, `MCP_API_KEY`) live in `.env` (gitignored). `GITLAB_TOKEN` stays inside `gitlab-mcp` only — agents never receive it. `.env.example` documents all required variables without values.

---

## GitLab CI/CD Pipeline

`.gitlab-ci.yml` defines 4 stages triggered on every push:

| Stage | Job | What it does |
|-------|-----|-------------|
| build | `backend-build` | `mvn clean compile` with Maven cache |
| build | `frontend-build` | `npm ci && npm run build` |
| test | `backend-test` | `mvn test` — publishes JUnit XML to GitLab |
| test | `frontend-test` | `npm test` |
| security | `security-scan` | OWASP dependency-check; fails only on CVSS ≥ 9 |
| notify | `pipeline-summary` | Logs branch, commit SHA, pipeline URL |

Every time DevLoop's FixAgent or SecurityAgent pushes a commit, a new pipeline run triggers — creating a live CI history on the MR.

---

## Key Design Decisions

**Why SequentialAgent?** Each agent depends on the previous one's output. Code must be written before tests, tests must pass before MR creation. Sequential is the correct topology.

**Why MCP for tools?** MCP decouples tool implementation from agent logic. Each MCP server can be tested independently, replaced, or extended without touching the agents.

**Why `read_file` before `write_file`?** The most common LLM code generation failure is ignoring existing code. DevAgent reads the full file first, then modifies it — preserving existing imports, annotations, and logic.

**Why H2 for the demo DB?** Zero infrastructure: the app starts with `mvn spring-boot:run` and the database is ready. IntegrationTestAgent can call the live API immediately.

---

## Course Key Concepts Demonstrated

Per the capstone evaluation criteria (minimum 3 required), DevLoop demonstrates:

| Key Concept | Where Demonstrated |
|-------------|-------------------|
| Multi-agent system (Google ADK) | Code — 10 `LlmAgent`s composed in a `SequentialAgent` pipeline (`agents/`) |
| MCP Server | Code — 5 custom stdio MCP servers with typed tool schemas (`mcp_servers/`) |
| Security features | Code — MCP API-key auth, path-traversal guards, OWASP CVE scan + auto-remediation |
| Deployability | Code + Video — `Dockerfile`, `docker-compose.yml`, 4-stage GitLab CI pipeline |
| Agent skills / vibe coding | Video — project built iteratively with AI-assisted coding per the course workflow |

---

## Known Limitations

- Performs best on additive changes (new fields, new endpoints). Complex refactoring requires more sophisticated prompting.
- Assumes a monorepo with `/backend` and `/frontend` directories.
- No merge conflict handling if `main` moves forward during the pipeline.
- Jira is mocked via local JSON files (production would use Jira REST API v3).

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent Framework | Google ADK 0.4+ |
| LLM | Gemini 2.5 Flash |
| Tool Protocol | MCP (Model Context Protocol) |
| Backend Demo | Java 21, Spring Boot 3.2, H2 |
| Frontend Demo | React 18, Vite, Axios |
| Source Control | GitLab REST API v4 |
| CI/CD | GitLab CI |
| Security Scanning | OWASP dependency-check |
| Language | Python 3.11+ |

---

## Links

- **Public repository:** https://gitlab.com/neelimabarji/devloop-demo
- **Live Merge Request produced by DevLoop:** https://gitlab.com/neelimabarji/devloop-demo/-/merge_requests/1
- **Video demo (YouTube, ≤5 min):** _[add link before submission]_
- **Kaggle Writeup:** see `KAGGLE_WRITEUP.md`

> 🔐 **No API keys or passwords are committed to this repository.** All secrets live in a gitignored `.env`; `.env.example` documents the required variables.

---

## Author

**Neelima Barji** — Kaggle × Google 5-Day AI Agents: Intensive Vibe Coding Capstone, 2026 (Agents for Business track).
