#!/bin/bash
# PUSH_TO_GITHUB.command: commits the King Health site and pushes it to GitHub (tealapexgroupjh/king-health).
# Cloudflare Pages deploys the public/ folder automatically after each push.
# Fallback: bash "/Users/tealapexgroup/TealApexGroup_Dev/01_Projects/Javon/King_Health/PUSH_TO_GITHUB.command"
set -u
chmod +x "$0" "${0%/*}"/*.command 2>/dev/null || true
REPO="/Users/tealapexgroup/TealApexGroup_Dev/01_Projects/Javon/King_Health"
REMOTE="git@github-tealapex:tealapexgroupjh/king-health.git"
cd "$REPO" || { echo "STOPPED. King_Health is not where this button expects it: $REPO"; exit 1; }
[ -d .git ] || git init -b main
git remote get-url origin >/dev/null 2>&1 || git remote add origin "$REMOTE"
git add -A
echo "Changes to publish:"
git status --short | head -40
if git diff --cached --quiet; then echo "Nothing new to commit."; else
  read -r -p "Commit these changes and push them to GitHub? Type y to continue: " ok
  [ "$ok" = "y" ] || { echo "Stopped. Nothing was committed."; read -r -p "Press Return to close..." _; exit 0; }
  read -r -p "Short description of the change (Return for a default): " msg
  git commit -q -m "${msg:-Update King Health site}" || { echo "STOPPED. Commit failed."; exit 1; }
fi
git push -u origin main && echo "Pushed. Cloudflare Pages will publish public/ in a minute or two." || echo "STOPPED. Push failed. Check that the GitHub repo tealapexgroupjh/king-health exists."
read -r -p "Press Return to close this window..." _
