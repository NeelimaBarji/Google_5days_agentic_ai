# DevLoop — 5-Minute Demo Video Script

**Target: 4:45 total.** Practice once with a timer; the demo section is pre-recorded/sped up so timing is safe.

**Recording plan:** screen recording (QuickTime/OBS) + voiceover. Pre-record the `devloop.py run PROD-1` terminal run beforehand and speed it up 8–10x for the demo section — never run it live.

---

## [0:00–0:35] Problem Statement
**On screen:** Title slide "DevLoop — Autonomous SDLC Agent", then a Jira-style ticket next to a GitLab MR with an arrow labeled "hours → days".

> Hi, I'm Neelima. In every software team, there's a huge gap between "the ticket is written" and "the code is merged." Even a routine change — adding one field to an API — means reading the ticket, exploring the codebase, writing code, writing tests, verifying the running system, opening a merge request, waiting for review, applying feedback, and passing a security scan. Hours to days of engineering time on steps that are well-defined and mechanical. That's real money for a business.

## [0:35–1:05] Why Agents?
**On screen:** Slide: "Why agents? Stateful workflow · hard dependencies · different tools per step · feedback loops".

> Why agents? Because a single LLM call can't do this. The development lifecycle is a stateful workflow with hard dependencies — code before tests, passing tests before a merge request, review before approval. Each step needs different tools and different expertise. And crucially, agents can react: when a test fails, the system reads the failure and repairs it. When review comments come in, it applies the fixes. That feedback loop is what makes this an agent problem.

## [1:05–1:50] Architecture
**On screen:** The architecture diagram from the README (zoom into each layer as you mention it).

> DevLoop is built on Google's Agent Development Kit. Ten specialized agents run in an ADK SequentialAgent pipeline: an Orchestrator reads and classifies the Jira ticket, an Analysis agent plans the change, a Dev agent writes the code, a Test Generator writes and self-heals unit tests, an Integration Test agent calls the live API, then agents create the merge request, review the diff with inline comments, apply the fixes, and run a security scan before approving.
>
> All tool access goes through five custom MCP servers — codebase, GitLab, API testing, security, and Jira. Each agent gets only the tools its role needs: the reviewer can't write files, the developer can't approve merge requests. Least privilege by design.

## [1:50–3:40] Demo (the core — spend the most time here)
**On screen:** Sped-up terminal recording of `python devloop.py run PROD-1`, then cut to GitLab in the browser.

> Let's watch it work. The ticket says: add a discount field to the Product entity and expose it via the API. One command: devloop run PROD-1.
>
> *(as terminal scrolls)* The Orchestrator classifies it as a backend change with six affected files. The Dev agent modifies the entity, the service, a database migration, and seed data — reading each file before writing, so existing code is preserved. The Test Generator writes eight unit tests and runs them to green. The Integration Test agent calls the live API — and there's the discount field in the real JSON response.
>
> *(switch to GitLab)* Now the GitLab side. Here's the merge request DevLoop opened — nine files pushed on branch feature/prod-1. Here are the two inline review comments it posted on its own diff… and the fix commit that addressed them, which re-triggered the CI pipeline: build, test, security scan — all green. OWASP found zero critical CVEs, and the MR is approved. Total time: seven minutes, one second — fully autonomous.

## [3:40–4:15] Security & Deployability
**On screen:** Split slide — left: `_check_auth()` + `safe_path()` code snippets; right: `docker-compose.yml` + GitLab CI pipeline view.

> Security is built in, not bolted on. Every MCP tool call is authenticated with an API key. Every file path is checked against path traversal. The security agent scans dependencies for CVEs and auto-remediates. And no secrets ever touch the repo — everything lives in a gitignored env file.
>
> For deployability, the whole system is containerized: one docker compose command brings up the backend, the frontend, and the agent, and a four-stage GitLab CI pipeline verifies every commit the agents push.

## [4:15–4:45] The Build & Close
**On screen:** Tech stack slide (ADK · Gemini 2.5 Flash · MCP · Spring Boot · React · GitLab CI), then final slide with repo URL.

> DevLoop was built with Google ADK and Gemini 2.5 Flash, using the vibe-coding workflow from the five-day course — iterating agent by agent. The biggest lessons: split one mega-agent into ten focused ones, force read-before-write, and feed test failures back to the agent that caused them.
>
> The code, the live merge request, and full setup instructions are in the public GitLab repo linked in the writeup. Thanks for watching!

---

## Shot checklist (record these before assembling)

- [ ] Terminal run of `python devloop.py run PROD-1` (full, then speed up in editing)
- [ ] GitLab MR page: files changed, inline review comments, fix commit, CI pipeline green, "Approved" badge
- [ ] `curl http://localhost:8080/api/products/1` showing `discount` in response
- [ ] Architecture diagram slide (export from README or draw in Excalidraw/Canva)
- [ ] Title + closing slides with repo URL
- [ ] Code close-ups: `orchestrator.py` (SequentialAgent), `_check_auth()`, `safe_path()`

## Recording tips

- 140–150 spoken words/minute — this script is ~640 words ≈ 4:20 of narration, leaving breathing room.
- Record narration separately from screen capture; sync in iMovie/CapCut/Clipchamp.
- Upload to YouTube as **Unlisted** (judges can view without it being fully public).
- Export at 1080p; make terminal font ≥16pt so it's readable.
