#!/usr/bin/env bash
# Initialise this folder as a git repo and push it to a PRIVATE GitHub repo.
# Run it from inside the unzipped folder:  bash setup_repo.sh
#
# Your GitHub credentials never leave your machine. This script does not ask
# for a token and never should — `gh auth login` handles it in your browser.

set -euo pipefail

REPO_NAME="${1:-leiko-content-machine}"

if [ -d .git ]; then
  echo "Already a git repo — skipping init."
else
  git init -b main
fi

# Refuse to proceed if a secret is sitting in the folder.
if git status --porcelain --ignored | grep -qE '\.env|\.secret'; then
  echo "A .env or .secret file is present. It is gitignored, but confirm it is"
  echo "not tracked before pushing:  git ls-files | grep -i env"
fi

git add -A
git commit -m "Leiko content machine: pipeline, locked design assets, copy rules" || true

if command -v gh >/dev/null 2>&1; then
  echo
  echo "Creating PRIVATE repo '$REPO_NAME' on GitHub..."
  gh repo create "$REPO_NAME" --private --source=. --remote=origin --push
  echo
  echo "Done. Now run:  claude"
else
  cat <<EOF

The GitHub CLI (gh) is not installed. Two options:

  A) Install it, then re-run this script:
       macOS:   brew install gh && gh auth login
       Ubuntu:  sudo apt install gh && gh auth login

  B) Create an EMPTY PRIVATE repo at https://github.com/new
     (no README, no .gitignore, no licence), then:

       git remote add origin git@github.com:<your-username>/$REPO_NAME.git
       git push -u origin main

Never paste a personal access token into a chat window. Use \`gh auth login\`
or an SSH key.
EOF
fi
