"""
Fix for failed CI job (npm ci exit 1) on feature/prod-2.

Root cause: remote master's frontend/package.json and package-lock.json are
out of sync (an earlier agent run pushed one without the other), so `npm ci`
fails on any branch cut from master.

This pushes the LOCAL, verified-in-sync frontend config + test files to
feature/prod-2 in a single commit, then the MR pipeline will re-run green.

Run:  python push_frontend_fix.py [branch]   (default: feature/prod-2)
"""

import os
import sys
import httpx
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

GITLAB_URL = os.environ.get("GITLAB_URL", "https://gitlab.com")
TOKEN = os.environ["GITLAB_TOKEN"]
PROJECT_ID = os.environ["GITLAB_PROJECT_ID"]
BRANCH = sys.argv[1] if len(sys.argv) > 1 else "feature/prod-2"
HEADERS = {"PRIVATE-TOKEN": TOKEN}
API = f"{GITLAB_URL}/api/v4/projects/{PROJECT_ID}"

FILES = [
    ".gitlab-ci.yml",
    "frontend/package.json",
    "frontend/package-lock.json",
    "frontend/babel.config.js",
    "frontend/jest.config.js",
    "frontend/src/setupTests.js",
    "frontend/src/__tests__/ProductList.test.jsx",
    "frontend/src/App.css",
]


def exists_on_branch(path: str) -> bool:
    r = httpx.get(f"{API}/repository/files/{quote(path, safe='')}",
                  params={"ref": BRANCH}, headers=HEADERS)
    return r.status_code == 200


def main():
    actions = []
    for path in FILES:
        if not os.path.exists(path):
            print(f"  ⚠️  skipping (not found locally): {path}")
            continue
        action = "update" if exists_on_branch(path) else "create"
        actions.append({
            "action": action,
            "file_path": path,
            "content": open(path, encoding="utf-8").read(),
        })
        print(f"  {action:>6}: {path}")

    r = httpx.post(f"{API}/repository/commits", headers=HEADERS, json={
        "branch": BRANCH,
        "commit_message": "Fix CI: sync package-lock.json with package.json; add jest config + tests",
        "actions": actions,
    }, timeout=60)

    if r.status_code == 201:
        sha = r.json()["short_id"]
        print(f"\n✅ Committed {len(actions)} files to {BRANCH} ({sha}). CI pipeline will re-run.")
        print(f"   Watch it: {GITLAB_URL.rstrip('/')}/neelimabarji/devloop-demo/-/merge_requests/2/pipelines")
    else:
        print(f"\n❌ Failed: {r.status_code} {r.text[:300]}")


if __name__ == "__main__":
    main()
