# DevLoop — Autonomous SDLC Agent for Java Spring Boot

> **Google 5-Day Agentic AI Intensive — Kaggle Capstone Project**
> **Track:** Agents for Business
> **Author:** Neelima Barji
> **Deadline:** July 6, 2026

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Solution Overview](#2-solution-overview)
3. [Requirements](#3-requirements)
4. [System Architecture](#4-system-architecture)
5. [Agent Design](#5-agent-design)
6. [MCP Server Design](#6-mcp-server-design)
7. [Demo Application](#7-demo-application)
8. [Implementation Details](#8-implementation-details)
9. [Security](#9-security)
10. [Deployability](#10-deployability)
11. [Evaluation](#11-evaluation)
12. [Capstone Checklist Coverage](#12-capstone-checklist-coverage)
13. [Limitations & Future Work](#13-limitations--future-work)
14. [Setup & Running](#14-setup--running)

---

## 1. Problem Statement

### The Reality of a Software Engineer's Day

A software engineer receives a Jira ticket:

> *"PROD-1: Add a `discount` field to the Product entity and expose it via the API."*

Before a single line of code is written, the engineer must:

1. Read and interpret the ticket's acceptance criteria
2. Identify which files need to change across the codebase
3. Write the implementation (entity, repository, service, controller)
4. Write unit tests for every new method and endpoint
5. Run tests and fix failures
6. Perform integration testing against the live backend or frontend
7. Create a test evidence document for QA
8. Create a Git branch, commit, push, and open a Merge Request
9. Wait for a senior engineer to review — then fix all review comments
10. Push the fixes, get re-approval
11. Scan `pom.xml` for any newly introduced CVEs and fix them
12. Watch the GitLab CI/CD pipeline pass

For a *single small ticket*, this process can take 3–6 hours of a senior engineer's day. In a team of 10 delivering 50 tickets a sprint, this overhead compounds into thousands of engineering hours per year — hours spent on process, not on creative problem-solving.

### The Opportunity

Large Language Models are now capable of reading code, generating code, reasoning about APIs, and acting autonomously. The emergence of multi-agent frameworks (Google ADK) and tool protocols (MCP) makes it possible to orchestrate these capabilities into a reliable, auditable pipeline that handles the full SDLC — not just code generation, but the complete workflow from ticket to merged, tested, secure code.

**DevLoop** is that pipeline.

---

## 2. Solution Overview

DevLoop is a **multi-agent autonomous SDLC system** built on Google's Agent Development Kit (ADK). It accepts a Jira ticket ID and autonomously executes the complete software development lifecycle:

```
Input: python devloop.py run PROD-1
         ↓
  [Read Jira Ticket]
         ↓
  [Analyze Codebase]
         ↓
  [Generate Code Changes]
         ↓
  [Write & Run Unit Tests]
         ↓
  [Run Integration Tests against Live API/UI]
         ↓
  [Generate Test Evidence Document]
         ↓
  [Create GitLab Branch + Push + Open MR]
         ↓
  [Review MR Diff — Post Comments]
         ↓
  [Apply Review Fixes + Re-push]
         ↓
  [Scan pom.xml for CVEs — Auto-fix]
         ↓
Output: ✅ MR created, pipeline green, CVEs fixed
```

**What makes DevLoop different from a code generator:**
- It operates on a *real, running codebase* — not a blank slate
- It understands the existing patterns and follows them
- It performs *real* integration tests against a live running API
- It interacts with the real GitLab API — branches, MRs, comments, approvals
- It scans and fixes real security vulnerabilities in `pom.xml`
- The GitLab CI/CD pipeline triggers automatically on every push

---

## 3. Requirements

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | System accepts a Jira ticket ID as CLI input | Must Have |
| FR-02 | System reads ticket title, description, and acceptance criteria | Must Have |
| FR-03 | System classifies change as BACKEND (Spring Boot) or FRONTEND (React) | Must Have |
| FR-04 | System identifies which source files need to be created or modified | Must Have |
| FR-05 | System generates correct, compilable code changes maintaining existing style | Must Have |
| FR-06 | System writes unit tests for every new method/endpoint | Must Have |
| FR-07 | System executes unit tests and fixes failures before proceeding | Must Have |
| FR-08 | For BACKEND changes: system calls the live API to verify the new functionality | Must Have |
| FR-09 | For FRONTEND changes: system calls the backend API to verify data contract | Must Have |
| FR-10 | System generates a structured test evidence document (Markdown) | Must Have |
| FR-11 | System creates a feature branch and pushes all changed files to GitLab | Must Have |
| FR-12 | System creates a Merge Request with a descriptive title and body | Must Have |
| FR-13 | GitLab CI/CD pipeline triggers automatically on every push | Must Have |
| FR-14 | System reviews the MR diff and posts at minimum 2 actionable review comments | Must Have |
| FR-15 | System applies fixes for each review comment and pushes | Must Have |
| FR-16 | System scans `pom.xml` for CVEs using OWASP dependency-check | Must Have |
| FR-17 | System auto-fixes vulnerable dependency versions in `pom.xml` | Must Have |
| FR-18 | System posts a security scan summary comment on the MR | Must Have |
| FR-19 | System approves the MR after all fixes are applied | Should Have |

### 3.2 Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-01 | Pipeline completes end-to-end for a simple ticket | < 5 minutes |
| NFR-02 | Agent reasoning is transparent — each step is logged | Always |
| NFR-03 | All API credentials stored in environment variables | Always |
| NFR-04 | MCP server API key validated on every request | Always |
| NFR-05 | Generated code must compile (`mvn compile`) before MR is raised | Must Pass |
| NFR-06 | System is runnable locally and deployable via Docker | Both |
| NFR-07 | All agent tool calls auditable in session logs | Always |

### 3.3 Jira Demo Tickets

Three real tickets are included that exercise all agent paths:

**PROD-1 — Add `discount` field to Product (BACKEND)**
Add a `discount` (BigDecimal, 0.0–1.0) field to the Product entity, persist it, and expose it through all CRUD endpoints. Integration test: call `GET /api/products/1` and verify `discount` is present in the JSON response.

**PROD-2 — Add status filter to product list (FRONTEND)**
Add a status filter dropdown (ALL / ACTIVE / INACTIVE / DISCONTINUED) to the product list page. Integration test: call `GET /api/products?status=ACTIVE` and verify it returns only active products — confirming the data contract the new UI depends on is intact.

**PROD-3 — Add `GET /api/products/low-stock` endpoint (BACKEND)**
New endpoint returning products with stock below a configurable threshold (default 10). Integration test: call the new endpoint and verify the response includes only products with `stock < threshold`.

---

## 4. System Architecture

### 4.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER / CLI                              │
│              python devloop.py run PROD-1                       │
└───────────────────────────────┬─────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────┐
│                    DEVLOOP AGENT LAYER (Python / ADK)           │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   SequentialAgent Pipeline               │  │
│  │                                                          │  │
│  │  OrchestratorAgent → AnalysisAgent → DevAgent           │  │
│  │      → TestGeneratorAgent → IntegrationTestAgent        │  │
│  │      → TestDocAgent → MRAgent → ReviewAgent             │  │
│  │      → FixAgent → SecurityAgent                         │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Shared Session State (ADK InMemorySessionService)             │
│  pipeline_context | change_plan | dev_output | test_results    │
│  integration_test_results | mr_details | review_results        │
│  fix_results | security_results                                │
└────────┬──────────────────────────────────────┬────────────────┘
         │ MCP Protocol                          │ MCP Protocol
┌────────▼──────────┐              ┌─────────────▼──────────────┐
│   codebase-mcp    │              │       gitlab-mcp            │
│ ─────────────── │              │ ──────────────────────────  │
│ read_file         │              │ create_branch               │
│ write_file        │              │ push_file                   │
│ list_files        │              │ create_mr                   │
│ run_maven_tests   │              │ get_mr_diff                 │
│ run_frontend_tests│              │ post_mr_comment             │
└────────┬──────────┘              │ approve_mr                  │
         │                         │ get_pipeline_status         │
┌────────▼──────────┐              └─────────────┬──────────────┘
│   api-test-mcp    │                            │
│ ─────────────── │              ┌─────────────▼──────────────┐
│ http_get          │              │       security-mcp          │
│ http_post         │              │ ──────────────────────────  │
│ http_put          │              │ scan_pom                    │
│ verify_response   │              │ get_safe_version            │
└────────┬──────────┘              └─────────────────────────────┘
         │
┌────────▼──────────┐              ┌────────────────────────────┐
│   jira-mcp        │              │   DEMO APPLICATION          │
│ ─────────────── │              │ ──────────────────────────  │
│ get_ticket        │              │ Spring Boot :8080           │
│ update_ticket_    │              │ React UI    :3000           │
│   status          │              │ GitLab CI/CD Pipeline       │
└───────────────────┘              └────────────────────────────┘
```

### 4.2 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Agent Framework | Google ADK 0.4+ | LlmAgent, SequentialAgent, session state |
| LLM | Gemini 2.0 Flash | Agent reasoning for all 9 agents |
| Tool Protocol | MCP (Model Context Protocol) | Expose tools to agents |
| Backend Demo App | Java 17, Spring Boot 3.2 | The codebase DevLoop modifies |
| Frontend Demo App | React 18, Axios | UI that consumes the backend API |
| Source Control | GitLab | Branch/MR/pipeline management |
| CI/CD | GitLab CI | Auto-triggered on every push |
| Security Scanning | OWASP dependency-check | pom.xml CVE detection |
| Containerization | Docker, Docker Compose | Local deployment |
| Language | Python 3.11+ | All agent and MCP server code |

### 4.3 Data Flow — BACKEND Change (PROD-1)

```
1. User runs: python devloop.py run PROD-1
2. OrchestratorAgent → reads PROD-1.json → classifies: BACKEND
3. AnalysisAgent → reads Product.java, ProductService.java,
                   ProductController.java → creates change_plan
4. DevAgent → reads each file → adds discount field → writes files
5. TestGeneratorAgent → writes new JUnit test → runs mvn test → PASS
6. IntegrationTestAgent → calls GET http://localhost:8080/api/products/1
                       → verifies "discount" in response → PASS
7. TestDocAgent → writes test-reports/PROD-1-test-report.md
8. MRAgent → create_branch(feature/prod-1) → push_file(×4 files)
           → create_mr("[PROD-1] Add discount field to Product")
           → GitLab CI pipeline triggers automatically ↻
9. ReviewAgent → get_mr_diff() → posts 2 review comments
10. FixAgent → reads comments → applies fixes → push_file → pipeline ↻
11. SecurityAgent → scan_pom() → no CVEs → posts "✅ Security scan passed"
                → approve_mr()

Output: GitLab MR #3 open, pipeline green, approved
```

### 4.4 Data Flow — FRONTEND Change (PROD-2)

```
1. User runs: python devloop.py run PROD-2
2. OrchestratorAgent → classifies: FRONTEND
3. AnalysisAgent → reads ProductList.jsx, api.js,
                   ProductController.java (needs ?status= param added)
4. DevAgent → adds status filter dropdown to ProductList.jsx
            → adds status param to api.js → adds @RequestParam to Controller
5. TestGeneratorAgent → writes Jest/RTL test → runs npm test → PASS
6. IntegrationTestAgent → (FRONTEND path) → calls backend API:
     GET http://localhost:8080/api/products?status=ACTIVE
     → verifies all returned products have status=ACTIVE
     → verifies the data contract the new UI component depends on
7. TestDocAgent → writes test-reports/PROD-2-test-report.md
8. MRAgent → pushes all changed files → creates MR → pipeline triggers ↻
9. ReviewAgent → reviews → posts comments (e.g., missing loading state reset)
10. FixAgent → applies fixes → pushes → pipeline ↻ → approves MR
11. SecurityAgent → scan_pom() → posts security status
```

---

## 5. Agent Design

### 5.1 OrchestratorAgent

**Role:** Entry point. Reads the Jira ticket, classifies the change type, and produces the `pipeline_context` that all downstream agents consume.

**Model:** `gemini-2.0-flash`
**Tools:** `get_ticket` (via jira-mcp)
**Output key:** `pipeline_context`

**Classification logic:**
- BACKEND → new API endpoint, new entity field, business logic, DB schema change
- FRONTEND → new UI component, filter/search, form field, display change

**Output schema:**
```json
{
  "ticket_id": "PROD-1",
  "title": "Add discount field to Product",
  "description": "...",
  "acceptance_criteria": ["..."],
  "change_type": "BACKEND",
  "affected_files": ["entity/Product.java", "..."],
  "branch_name": "feature/prod-1"
}
```

---

### 5.2 AnalysisAgent

**Role:** Explorer. Reads the codebase to understand existing structure and produces a precise change plan.

**Model:** `gemini-2.0-flash`
**Tools:** `read_file`, `list_files` (via codebase-mcp)
**Output key:** `change_plan`

**Key behavior:** The agent does NOT assume file locations — it calls `list_files` first, then reads relevant files to understand existing patterns before proposing changes. This ensures generated code follows the project's established conventions.

**Output schema:**
```json
{
  "files_to_modify": [
    {
      "path": "backend/src/main/java/com/devloop/product/entity/Product.java",
      "action": "MODIFY",
      "changes_needed": "Add BigDecimal discount field with @DecimalMin(0.0) @DecimalMax(1.0) validation"
    }
  ],
  "implementation_notes": "Project uses Lombok @Data and @Builder. Follow same pattern."
}
```

---

### 5.3 DevAgent

**Role:** Engineer. Reads each file to be changed, applies the minimum necessary modification, writes the result.

**Model:** `gemini-2.0-flash`
**Tools:** `read_file`, `write_file` (via codebase-mcp)
**Output key:** `dev_output`

**Critical constraint:** The agent receives the *entire existing file content* before generating changes. This prevents the common LLM failure of generating code that ignores existing structure. The prompt explicitly instructs: "Never remove existing functionality — only ADD or MODIFY."

**For Spring Boot:** Maintains `@CrossOrigin`, `@Valid`, Lombok annotations, `@Transactional` scope.
**For React:** Maintains existing `useState`/`useEffect` patterns, error/loading states, CSS class names.

---

### 5.4 TestGeneratorAgent

**Role:** QA engineer. Writes tests for every new method/endpoint, runs them, fixes failures.

**Model:** `gemini-2.0-flash`
**Tools:** `read_file`, `write_file`, `run_maven_tests`, `run_frontend_tests` (via codebase-mcp)
**Output key:** `test_results`

**For BACKEND:** Adds test cases to `ProductControllerTest.java` using the established `@WebMvcTest + MockMvc + @MockBean` pattern. Tests cover: happy path, validation failure, not-found case.

**For FRONTEND:** Creates `__tests__/ProductList.test.jsx` using React Testing Library. Tests cover: component renders, filter triggers API call with correct params, empty state.

**Self-healing loop:** If `run_maven_tests()` returns FAILED, the agent reads the error output, fixes either the test or the source code, and re-runs. This loop continues until tests pass.

---

### 5.5 IntegrationTestAgent

**Role:** Integration tester. Tests the *actual running system* — not mocks.

**Model:** `gemini-2.0-flash`
**Tools:** `http_get`, `http_post`, `verify_response` (via api-test-mcp)
**Output key:** `integration_test_results`

**Decision logic:**
```
if change_type == "BACKEND":
    → Call the new/changed API endpoint directly
    → Verify response contains the new field/data
    Example: GET /api/products/1 → verify "discount" in JSON

if change_type == "FRONTEND":
    → Call the backend API the new UI component depends on
    → Verify data contract is correct
    Example: GET /api/products?status=ACTIVE → verify all items have status=ACTIVE
```

**Why this split matters:** A backend change is tested by calling the API. A frontend change is tested by verifying the backend contract the frontend relies on — confirming the new filter will actually work when the UI makes the call.

---

### 5.6 TestDocAgent

**Role:** Technical writer. Converts raw test results into a structured evidence document.

**Model:** `gemini-2.0-flash`
**Tools:** `write_file` (via codebase-mcp)
**Output key:** `test_report_path`

Generates: `test-reports/PROD-1-test-report.md`

Structure: Summary table → Ticket details → Unit test results table → Integration test results table → Files changed → Coverage notes.

---

### 5.7 MRAgent

**Role:** DevOps. Pushes all changed files to GitLab and creates the Merge Request.

**Model:** `gemini-2.0-flash`
**Tools:** `create_branch`, `push_file`, `read_file`, `create_mr` (via gitlab-mcp)
**Output key:** `mr_details`

**MR body includes:** Summary of changes, list of modified files, test results, acceptance criteria checklist, and step-by-step testing instructions. Ends with: *"Raised automatically by DevLoop 🤖"*

**Important:** GitLab CI pipeline is triggered automatically when files are pushed to the branch — no manual trigger required.

---

### 5.8 ReviewAgent

**Role:** Senior engineer. Reviews the MR diff and posts actionable comments.

**Model:** `gemini-2.0-flash`
**Tools:** `get_mr_diff`, `post_mr_comment` (via gitlab-mcp)
**Output key:** `review_results`

**BACKEND review checks:** missing `@Valid`, missing null checks, missing `@Transactional`, no logging, missing `@Column` constraints, inconsistent naming.

**FRONTEND review checks:** missing loading/error states, no input validation, memory leaks in `useEffect`, missing `key` props, hardcoded strings.

Posts at least 2 inline review comments + 1 overall summary comment.

---

### 5.9 FixAgent

**Role:** Applies every review comment as a code fix, then pushes.

**Model:** `gemini-2.0-flash`
**Tools:** `read_file`, `write_file`, `push_file`, `post_mr_comment`, `approve_mr` (via gitlab-mcp + codebase-mcp)
**Output key:** `fix_results`

After all fixes are pushed (triggering the pipeline again), the agent posts a follow-up comment listing every fix applied, then calls `approve_mr`.

---

### 5.10 SecurityAgent

**Role:** Security engineer. Scans `pom.xml` for CVEs and auto-remediates.

**Model:** `gemini-2.0-flash`
**Tools:** `scan_pom`, `get_safe_version`, `read_file`, `write_file`, `push_file`, `post_mr_comment` (via security-mcp + codebase-mcp + gitlab-mcp)
**Output key:** `security_results`

Runs OWASP dependency-check against `pom.xml`. For each CVE found, queries the safe version registry and updates the dependency version directly in `pom.xml`. Posts a security table comment on the MR showing CVE ID, severity, vulnerable version, and fixed version.

---

## 6. MCP Server Design

MCP (Model Context Protocol) is used to expose all external tool capabilities to the ADK agents. Each MCP server is a Python process communicating over stdio.

### 6.1 codebase-mcp

Provides filesystem and test execution capabilities.

| Tool | Description | Input | Output |
|------|-------------|-------|--------|
| `read_file` | Read any project file | `path: str` | File contents as text |
| `write_file` | Write/overwrite a file | `path: str, content: str` | Confirmation |
| `list_files` | Recursively list directory | `directory: str` | Newline-separated paths |
| `run_maven_tests` | Run `mvn test` in /backend | — | PASSED/FAILED + output |
| `run_frontend_tests` | Run `npm test` in /frontend | — | PASSED/FAILED + output |

Excludes `node_modules`, `.git`, `target`, `__pycache__` from directory listings.

### 6.2 gitlab-mcp

Wraps the GitLab REST API v4. Requires `GITLAB_TOKEN` and `GITLAB_PROJECT_ID` environment variables.

| Tool | GitLab API | Description |
|------|-----------|-------------|
| `create_branch` | `POST /repository/branches` | Create feature branch from main |
| `push_file` | `PUT/POST /repository/files/:path` | Upsert a file on the branch |
| `create_mr` | `POST /merge_requests` | Open a new MR |
| `get_mr_diff` | `GET /merge_requests/:id/diffs` | Fetch diff for review |
| `post_mr_comment` | `POST /merge_requests/:id/notes` | Post review comment |
| `approve_mr` | `POST /merge_requests/:id/approve` | Approve MR |
| `get_pipeline_status` | `GET /pipelines/:id` | Check CI status |

### 6.3 api-test-mcp

HTTP client for integration testing. Talks to the running Spring Boot app at `localhost:8080`.

| Tool | Description |
|------|-------------|
| `http_get` | GET request with optional query params |
| `http_post` | POST request with JSON body |
| `http_put` | PUT request with JSON body |
| `verify_response` | Assert expected fields/values in a JSON response, returns PASS/FAIL with evidence |

### 6.4 security-mcp

OWASP dependency-check wrapper with safe-version registry fallback.

| Tool | Description |
|------|-------------|
| `scan_pom` | Run OWASP dependency-check on pom.xml; returns list of CVEs with severity |
| `get_safe_version` | Return the latest non-vulnerable version for a given Maven artifact ID |

### 6.5 jira-mcp

Mock Jira using local JSON files (production version uses Jira REST API v3).

| Tool | Description |
|------|-------------|
| `get_ticket` | Read ticket JSON from `jira-tickets/<ID>.json` |
| `update_ticket_status` | Update `status` field in the ticket JSON |

---

## 7. Demo Application

### 7.1 Overview

**ProductFlow** — A product management system used as the target codebase for all DevLoop demo scenarios.

### 7.2 Backend: Spring Boot Product Service

**Entity:**
```java
Product {
    Long id
    String name           // required, max 200 chars
    String description    // optional, max 1000 chars
    BigDecimal price      // required, > 0
    String category       // ELECTRONICS | FURNITURE | STATIONERY
    Integer stock         // >= 0
    String sku            // required, unique
    ProductStatus status  // ACTIVE | INACTIVE | DISCONTINUED
    LocalDateTime createdAt
}
```

**Endpoints:**
```
GET    /api/products              → List all (optional ?category= filter)
GET    /api/products/{id}         → Get one product
POST   /api/products              → Create product
PUT    /api/products/{id}         → Update product
DELETE /api/products/{id}         → Delete product
GET    /api/products/low-stock    → Products with stock < threshold (default 10)
```

**Key design decisions:**
- H2 in-memory DB (dev) for zero infrastructure dependency during demo
- Spring Validation (`@Valid`, `@NotBlank`, `@DecimalMin`) on all inputs
- `@CrossOrigin(origins = "http://localhost:3000")` for React integration
- Lombok (`@Data`, `@Builder`, `@Slf4j`) throughout — agents maintain this pattern
- `data.sql` seeds 7 realistic products across 3 categories

### 7.3 Frontend: React Product Management UI

**Pages:**
- `/` — Product list with search bar, category filter tabs, low-stock warnings
- `/products/new` — Create product form with client-side validation
- `/products/:id` — Product detail view
- `/products/:id/edit` — Edit product form

**Notable features:**
- Category filter buttons (ALL / ELECTRONICS / FURNITURE / STATIONERY)
- Low-stock warning icon on rows with `stock < 10`
- Status badge with color coding (ACTIVE=green, INACTIVE=amber, DISCONTINUED=red)
- Search filters by name or SKU client-side

---

## 8. Implementation Details

### 8.1 Project Structure

```
devloop/
├── devloop.py                    ← CLI entry point
├── requirements.txt
├── .env.example
├── .gitlab-ci.yml
│
├── agents/
│   ├── orchestrator.py           ← SequentialAgent pipeline definition
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
│   └── jira_mcp.py
│
├── jira-tickets/
│   ├── PROD-1.json               ← Add discount field (BACKEND)
│   ├── PROD-2.json               ← Status filter UI (FRONTEND)
│   └── PROD-3.json               ← Low-stock endpoint (BACKEND)
│
├── test-reports/                 ← Generated by TestDocAgent per run
│
└── backend/                      ← Spring Boot project
│   ├── pom.xml
│   └── src/
│       ├── main/java/com/devloop/product/
│       │   ├── ProductApplication.java
│       │   ├── entity/Product.java
│       │   ├── repository/ProductRepository.java
│       │   ├── service/ProductService.java
│       │   └── controller/ProductController.java
│       ├── main/resources/
│       │   ├── application.yml
│       │   └── data.sql
│       └── test/java/com/devloop/product/
│           └── ProductControllerTest.java
│
└── frontend/                     ← React project
    ├── package.json
    └── src/
        ├── App.jsx
        ├── App.css
        ├── index.js
        ├── services/api.js
        └── components/
            ├── ProductList.jsx
            ├── ProductForm.jsx
            └── ProductDetail.jsx
```

### 8.2 ADK Session State Flow

ADK's `InMemorySessionService` passes data between agents via `output_key`. Each agent writes to a named key; downstream agents read from earlier keys via session context.

```
OrchestratorAgent   → writes: pipeline_context
AnalysisAgent       → reads: pipeline_context  | writes: change_plan
DevAgent            → reads: change_plan        | writes: dev_output
TestGeneratorAgent  → reads: dev_output         | writes: test_results
IntegrationTest     → reads: pipeline_context, dev_output | writes: integration_test_results
TestDocAgent        → reads: all test results   | writes: test_report_path
MRAgent             → reads: dev_output, test_report_path | writes: mr_details
ReviewAgent         → reads: mr_details         | writes: review_results
FixAgent            → reads: review_results, mr_details  | writes: fix_results
SecurityAgent       → reads: mr_details         | writes: security_results
```

### 8.3 Key Implementation Choices

**Why SequentialAgent instead of parallel execution?**
Each agent depends on the output of the previous one. Code must be written before tests, tests must pass before MR is raised, MR must exist before review can happen. Sequential is the correct topology.

**Why Gemini 2.0 Flash for all agents?**
Flash provides the best balance of speed and code generation quality for this pipeline. The bottleneck is sequential tool calls (file reads/writes, API calls), not LLM generation time.

**Why mock Jira with JSON files?**
For the capstone demo, real Jira auth adds setup friction with no additional demonstrative value. The `jira_mcp.py` is structured identically to what a real Jira REST API wrapper would look like — swapping the data source is a 20-line change.

**Why H2 for the demo database?**
Zero infrastructure: the Spring Boot app starts with `mvn spring-boot:run` and the database is ready. The IntegrationTestAgent can call the live API immediately without provisioning Postgres.

**Why `read_file` before `write_file` in DevAgent?**
The most common LLM code generation failure is ignoring existing code and generating a complete replacement from scratch. By explicitly reading the current file content first and including it in the agent's context, the DevAgent modifies rather than replaces — preserving existing imports, annotations, and logic.

---

## 9. Security

Security is a first-class concern in DevLoop, demonstrated in two places:

### 9.1 MCP Server API Key Validation

Every MCP server validates an `MCP_API_KEY` environment variable on startup. Tool calls without a matching key return an authentication error. This prevents unauthorized agents or processes from invoking the MCP servers.

```python
# In each MCP server
MCP_API_KEY = os.environ.get("MCP_API_KEY", "")

@app.call_tool()
async def call_tool(name: str, arguments: dict, context: dict):
    if context.get("api_key") != MCP_API_KEY:
        return [TextContent(type="text", text="ERROR: Unauthorized")]
    # ... proceed
```

### 9.2 Input Sanitization in codebase-mcp

File paths are validated to prevent path traversal attacks. Any path containing `..` or attempting to escape the project root is rejected.

```python
def safe_path(base: str, requested: str) -> str:
    resolved = os.path.realpath(os.path.join(base, requested))
    if not resolved.startswith(os.path.realpath(base)):
        raise ValueError("Path traversal detected")
    return resolved
```

### 9.3 pom.xml CVE Scanning (SecurityAgent)

The SecurityAgent runs OWASP dependency-check against `pom.xml` after every MR push. When CVEs are found:
1. `scan_pom()` returns CVE ID, severity, and affected artifact
2. `get_safe_version()` returns the patched version
3. Agent updates `pom.xml` directly and pushes the fix commit
4. Posts a security table on the MR

### 9.4 Credential Management

All sensitive values (GitLab token, Google API key, MCP API key) are stored in `.env` and never hardcoded. `.env` is in `.gitignore`. The `.env.example` file documents the required variables.

### 9.5 Spring Boot Security

The demo application uses Spring Boot Validation to sanitize all API inputs:
- `@NotBlank`, `@Size`, `@DecimalMin`, `@Min` on entity fields
- `@Valid` on all `@RequestBody` parameters in the controller
- Duplicate SKU check in the service layer

---

## 10. Deployability

### 10.1 Local Development

```bash
# 1. Clone and configure
git clone <your-gitlab-repo>
cp .env.example .env
# Fill in: GOOGLE_API_KEY, GITLAB_TOKEN, GITLAB_PROJECT_ID, PROJECT_ROOT

# 2. Start backend
cd backend && mvn spring-boot:run
# Spring Boot starts at localhost:8080

# 3. Start frontend
cd frontend && npm install && npm start
# React starts at localhost:3000

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Run DevLoop
python devloop.py run PROD-1
```

### 10.2 Docker Compose (Full Stack)

`docker-compose.yml` packages the entire demo:

```yaml
version: "3.9"
services:
  backend:
    build: ./backend
    ports:
      - "8080:8080"
    environment:
      - SPRING_PROFILES_ACTIVE=docker

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  devloop-agent:
    build: .
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - GITLAB_TOKEN=${GITLAB_TOKEN}
      - GITLAB_PROJECT_ID=${GITLAB_PROJECT_ID}
      - MCP_API_KEY=${MCP_API_KEY}
    volumes:
      - .:/workspace
    depends_on:
      - backend
      - frontend
    command: ["python", "devloop.py", "run", "PROD-1"]
```

```bash
docker compose up
# All 3 services start; DevLoop agent runs PROD-1 automatically
```

### 10.3 GitLab CI/CD Pipeline

The `.gitlab-ci.yml` defines 4 stages triggered on every push to any branch:

**Stage 1: Build**
- `backend-build`: `mvn clean compile` with Maven cache
- `frontend-build`: `npm ci && npm run build` with node_modules cache

**Stage 2: Test**
- `backend-test`: `mvn test` — publishes JUnit XML reports to GitLab
- `frontend-test`: `npm test -- --watchAll=false`

**Stage 3: Security**
- `security-scan`: OWASP dependency-check on `pom.xml`
- Reports stored as GitLab artifacts, fails only on CVSS ≥ 9

**Stage 4: Notify**
- `pipeline-summary`: Logs branch, commit SHA, and pipeline URL

Every time DevLoop's FixAgent or SecurityAgent pushes a commit, a new pipeline run is triggered — creating a live, auditable CI history for the MR.

### 10.4 GCP Cloud Run Deployment (Optional)

For the video demo, the Spring Boot backend can be deployed to GCP Cloud Run:

```bash
# Build and push image
gcloud builds submit --tag gcr.io/<PROJECT_ID>/product-service ./backend

# Deploy to Cloud Run
gcloud run deploy product-service \
  --image gcr.io/<PROJECT_ID>/product-service \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated

# Update .env with the Cloud Run URL
BACKEND_URL=https://product-service-xxxx.run.app
```

---

## 11. Evaluation

### 11.1 Evaluation Criteria

DevLoop is evaluated against three dimensions:

**A. Pipeline Correctness — Does the generated code actually work?**

| Scenario | Pass Condition |
|----------|---------------|
| PROD-1 (add `discount` field) | `mvn compile` succeeds; `GET /api/products/1` returns `discount` in JSON |
| PROD-2 (status filter UI) | `npm build` succeeds; `GET /api/products?status=ACTIVE` returns only ACTIVE products |
| PROD-3 (low-stock endpoint) | `GET /api/products/low-stock?threshold=5` returns products with stock < 5 |

**B. Agent Reasoning Quality — Does each agent do the right thing?**

| Agent | Evaluation Check |
|-------|-----------------|
| OrchestratorAgent | Correctly classifies PROD-1 and PROD-3 as BACKEND, PROD-2 as FRONTEND |
| AnalysisAgent | Identifies all and only the necessary files (no hallucinated paths) |
| DevAgent | Generated code compiles, follows existing patterns, no regressions |
| TestGeneratorAgent | Tests actually test the new functionality, not generic boilerplate |
| IntegrationTestAgent | Calls the correct endpoint with correct params; PASS/FAIL is accurate |
| ReviewAgent | Comments are about the actual diff, not generic advice |
| FixAgent | Each fix addresses the specific comment it claims to fix |
| SecurityAgent | CVE table matches actual dependency-check output |

**C. E2E Flow — Does the GitLab side work?**

| Check | Expected |
|-------|----------|
| Branch created | `feature/prod-1` visible in GitLab |
| Files pushed | All changed files present on the branch |
| MR created | MR open with correct title and description |
| Pipeline triggered | CI pipeline runs automatically, passes |
| Review comments | At least 2 comments posted on MR |
| Fix commits | Additional commit(s) visible on branch |
| Security comment | Security scan result posted on MR |
| MR approved | MR shows "Approved" status |

### 11.2 Test Results (Expected for Demo)

**PROD-1 — Unit Tests:**
```
Tests run: 5, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS
```

**PROD-1 — Integration Tests:**
```
✅ GET /api/products/1 → HTTP 200
✅ Field 'discount' present: 0.15
✅ Field 'name' present: Wireless Mouse
Verification: PASS
```

**PROD-2 — Frontend Tests:**
```
PASS src/__tests__/ProductList.test.jsx
  ✓ renders product list
  ✓ status filter calls API with status param (23ms)
  ✓ empty state shown when no products match
Test Suites: 1 passed, 1 total
```

**PROD-2 — Integration Tests:**
```
✅ GET /api/products?status=ACTIVE → HTTP 200, 5 products
✅ All products have status=ACTIVE
Verification: PASS
```

### 11.3 Limitations Discovered During Testing

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| DevAgent may generate syntactically valid but logically wrong code for complex business rules | Medium | Scope demo tickets to additive changes (new fields, new endpoints) |
| OWASP dependency-check takes 2–3 minutes on first run (downloads CVE database) | Low | Pre-warm the database; fallback to static version check for demo |
| IntegrationTestAgent assumes Spring Boot is running at localhost:8080 | Medium | Add startup check; if not running, start it via codebase-mcp shell tool |
| GitLab MR approval requires the token user to not be the MR author | Low | Use a separate "DevLoop Bot" GitLab user for the token |

---

## 12. Capstone Checklist Coverage

| Requirement | Implementation | Evidence Location |
|-------------|---------------|-------------------|
| ✅ **Multi-agent system (ADK)** | 9 LlmAgents composed in a SequentialAgent pipeline. Each agent has a distinct role and communicates via ADK session state | `agents/orchestrator.py` — `devloop_pipeline = SequentialAgent(sub_agents=[...])` |
| ✅ **MCP Server** | 5 MCP servers (codebase, gitlab, api-test, security, jira) exposing 20+ tools to agents | `mcp_servers/` directory; all use `mcp.server.Server` with `@app.list_tools()` and `@app.call_tool()` |
| ✅ **Security Features** | (1) API key validation in MCP servers; (2) Path traversal prevention in codebase-mcp; (3) pom.xml CVE scanning + auto-remediation by SecurityAgent | `mcp_servers/codebase_mcp.py`, `mcp_servers/security_mcp.py`, `agents/security_agent.py` |
| ✅ **Deployability** | Docker Compose packages full stack; GitLab CI/CD pipeline runs on every push; GCP Cloud Run deployment documented | `.gitlab-ci.yml`, `docker-compose.yml`, Section 10 |
| ✅ **Agent Skills / CLI** | `devloop.py` provides a CLI entry point: `python devloop.py run PROD-1`. Single command triggers the entire 10-agent pipeline | `devloop.py` |

**Score target: 5 of 6 checklist items covered (minimum required: 3)**

### Competition Track

**Agents for Business** — DevLoop directly addresses a high-value enterprise problem: the productivity overhead of the software development lifecycle. Every Java shop with a Jira board and a GitLab repo is a potential user.

---

## 13. Limitations & Future Work

### Current Limitations

**Code generation scope:** DevLoop performs best on *additive* changes — new fields, new endpoints, new UI components. Complex refactoring (renaming abstractions, changing inheritance hierarchies) requires more sophisticated reasoning than the current agent prompts provide.

**Single codebase assumption:** The current implementation assumes a monorepo with `/backend` and `/frontend` directories. Multi-repo projects would need updates to the codebase-mcp path resolution.

**No merge conflict handling:** If the main branch has moved forward while the feature branch was being built, the MRAgent will fail to push. A conflict resolution loop is not yet implemented.

**Integration test coverage:** The IntegrationTestAgent tests the primary happy path. It does not generate exhaustive negative test scenarios (e.g., invalid input to the new endpoint).

### Future Work

| Feature | Description | Priority |
|---------|-------------|----------|
| Real Jira integration | Replace JSON mock with Jira REST API v3 | High |
| Parallel sub-agents | Run Analysis + Security scan in parallel before Dev starts | Medium |
| Test coverage enforcement | Block MR creation if unit test coverage drops below threshold | Medium |
| Multi-repo support | Accept a GitHub/GitLab project URL instead of local path | Medium |
| Slack/Teams notification | Post pipeline summary to a channel | Low |
| Support for other frameworks | Extend DevAgent to handle Quarkus, Micronaut, Next.js | Low |
| Human-in-the-loop option | Pause before MR creation for human review approval | Low |
| Memory across runs | Persist codebase patterns learned from one ticket to inform the next | High |

---

## 14. Setup & Running

### Prerequisites

- Python 3.11+
- Java 17+ and Maven 3.9+
- Node.js 20+
- GitLab account with a project (free tier works)
- Google AI Studio API key (for Gemini 2.0 Flash)

### Step-by-Step Setup

**1. Clone the repository**
```bash
git clone https://gitlab.com/<your-username>/devloop.git
cd devloop
```

**2. Configure environment**
```bash
cp .env.example .env
```
Edit `.env`:
```
GOOGLE_API_KEY=<from aistudio.google.com>
GITLAB_TOKEN=<GitLab Personal Access Token with api scope>
GITLAB_PROJECT_ID=<numeric project ID from GitLab project settings>
PROJECT_ROOT=/absolute/path/to/devloop
MCP_API_KEY=<any random secret string>
```

**3. Install Python dependencies**
```bash
pip install -r requirements.txt
```

**4. Start the demo application**
```bash
# Terminal 1 — Backend
cd backend && mvn spring-boot:run
# Wait for: "Started ProductApplication in X seconds"

# Terminal 2 — Frontend
cd frontend && npm install && npm start
# Opens browser at localhost:3000
```

**5. Verify the app is running**
```bash
curl http://localhost:8080/api/products
# Should return a JSON array of 7 products
```

**6. Run DevLoop**
```bash
# Terminal 3 — DevLoop agent
python devloop.py run PROD-1
```

Watch the output as each agent fires in sequence. In 3–5 minutes, a new GitLab MR will be created at your project URL.

### Running All Three Demo Scenarios

```bash
python devloop.py run PROD-1   # Backend: add discount field
python devloop.py run PROD-2   # Frontend: add status filter
python devloop.py run PROD-3   # Backend: low-stock endpoint
```

### Running with Docker Compose

```bash
docker compose up --build
```

---

## Summary

DevLoop demonstrates that a multi-agent system built on Google ADK can autonomously execute the complete software development lifecycle for real-world Java Spring Boot projects. By combining 9 specialized agents with 5 MCP servers that interact with real systems (GitLab, live APIs, OWASP scanner), DevLoop moves beyond code generation into genuine engineering automation.

The project covers 5 of the 6 capstone checklist items, targets the Agents for Business track, and is backed by a working demo application with 3 representative Jira tickets that exercise every agent path in the pipeline.

---

*DevLoop — From Jira ticket to merged, tested, secure code. Autonomously.*
