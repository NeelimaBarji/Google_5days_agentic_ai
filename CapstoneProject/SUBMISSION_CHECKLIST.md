# Kaggle Submission Checklist — DevLoop

Deadline: **July 6, 2026, 11:59 PM PT** (you have ~2 days)
Competition: https://www.kaggle.com/competitions/vibecoding-agents-capstone-project

## 🚨 DO FIRST — Security (rubric penalizes API keys in code)

- [ ] **REVOKE the GitLab token immediately.** A real personal access token (`glpat-...`) was committed in `push-to-gitlab.sh` and is in your public repo's history AND in `.git/config` (remote URL). Go to GitLab → Settings → Access Tokens → revoke it, create a new one.
- [x] `push-to-gitlab.sh` fixed locally — now reads `${GITLAB_TOKEN}` from environment.
- [ ] Update your local remote so the new token isn't stored in the URL:
      `git remote set-url origin https://gitlab.com/neelimabarji/devloop-demo.git` (use a credential helper for auth)
- [ ] Commit and push the sanitized `push-to-gitlab.sh`:
      `git add push-to-gitlab.sh && git commit -m "Remove hardcoded token" && git push`
- [ ] (Optional but ideal) Rewrite history to purge the old token, or rely on revocation making it useless.
- [x] `.env` is gitignored and NOT in the repo — verified.
- [x] No other hardcoded keys found in tracked files — verified via scan.

## Rubric audit — how the project scores

**Required: ≥3 course key concepts** — you have 4–5 ✅
| Concept | Where | Status |
|---|---|---|
| Multi-agent system (ADK) | `agents/` — 10 LlmAgents in a SequentialAgent | ✅ Code |
| MCP Server | `mcp_servers/` — 5 custom stdio servers | ✅ Code |
| Security features | API-key auth, safe_path, OWASP scan | ✅ Code (show in video too) |
| Deployability | Dockerfile, docker-compose, .gitlab-ci.yml | ⚠️ Must show in VIDEO |
| Antigravity / Agent skills | — | ⚠️ Show in video if you used them |

**Category 1 — The Pitch (30 pts)**
- Core Concept & Value (10): Strong — clear business value, agents central. ✅
- YouTube Video (10): ❌ **Not done — required.** Record ≤5 min covering: problem → why agents → architecture diagram → live demo of `python devloop.py run PROD-1` + the resulting MR → the build (ADK, MCP, Gemini, Docker/CI for deployability).
- Writeup (10): ✅ `KAGGLE_WRITEUP.md` ready (~1,400 words, under the 2,500 limit).

**Category 2 — Implementation (70 pts)**
- Technical Implementation (50): ✅ Multi-agent + MCP + self-healing tests + review loop; code has docstrings/comments. Fix the token issue above.
- Documentation (20): ✅ README covers problem, solution, architecture diagram, setup steps, security, CI. Consider adding a screenshot/architecture image.

## Submission steps on Kaggle

1. [ ] Record and upload the demo video to **YouTube** (public or unlisted, ≤5 min).
2. [ ] Create a **cover image** (required to submit) — e.g., the architecture diagram or a DevLoop banner.
3. [ ] Go to the competition → Writeups → **New Writeup**.
4. [ ] Paste `KAGGLE_WRITEUP.md` content; set title + subtitle; select track **Agents for Business**.
5. [ ] Media Gallery: attach the cover image and the YouTube video.
6. [ ] Attach the **Project Link**: https://gitlab.com/neelimabarji/devloop-demo (verify the repo is **Public** — open it in an incognito window).
7. [ ] Replace `[ADD YOUR YOUTUBE LINK]` in the writeup with the real link.
8. [ ] Save, then click **Submit** (a saved draft does NOT count — it must be submitted).

## Nice-to-have (if time permits)

- [ ] Add the architecture diagram as a PNG in the repo and in the Kaggle media gallery.
- [ ] Verify `git clone` + README setup steps work from scratch on a clean machine.
- [ ] Double-check the live MR link is publicly viewable.
