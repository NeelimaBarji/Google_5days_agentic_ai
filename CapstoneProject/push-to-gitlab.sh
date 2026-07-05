#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "🚀 DevLoop — Pushing to GitLab..."

# Load GITLAB_TOKEN from .env (gitignored — never hardcode secrets in this script)
if [ -f .env ]; then
  export $(grep -E '^GITLAB_TOKEN=' .env | xargs)
fi

if [ -z "$GITLAB_TOKEN" ]; then
  echo "❌ GITLAB_TOKEN not set. Add it to .env or export it, then re-run."
  exit 1
fi

# Clean up any stale git lock files
rm -f .git/index.lock 2>/dev/null || true

# Remove any existing .git if re-running
if [ -d ".git" ]; then
  echo "Removing existing .git folder..."
  rm -rf .git
fi

git init
git config user.email "neelimabarji32@gmail.com"
git config user.name "Neelima Barji"
git branch -M main

# GITLAB_TOKEN must be set in your environment (never hardcode it here)
git remote add origin "https://neelimabarji:${GITLAB_TOKEN}@gitlab.com/neelimabarji/devloop-demo.git"

git add .
git commit -m "Initial commit: DevLoop autonomous SDLC agent + ProductFlow demo app"
git push -u origin main

echo ""
echo "✅ Done! View your repo at: https://gitlab.com/neelimabarji/devloop-demo"
