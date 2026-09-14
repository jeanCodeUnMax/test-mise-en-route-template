#!/usr/bin/env bash
set -euo pipefail
TARGET="${1:-.}"
SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DST="$(cd "$TARGET" && pwd)"
for item in .agent .hephaistos .githooks scripts docs evidence .watchdog.json hephaistos.cmd hephaistos.ps1 AGENTS.md CLAUDE.md; do
  [ -e "$SRC/$item" ] && cp -R "$SRC/$item" "$DST/"
done
if [ -d "$DST/.git" ]; then
  git -C "$DST" config core.hooksPath .githooks || true
  chmod +x "$DST/.githooks/pre-commit" "$DST/.githooks/commit-msg" "$DST/.githooks/pre-push" 2>/dev/null || true
  chmod +x "$DST/install-hephaistos.sh" 2>/dev/null || true
fi
echo '✅ HEPHAISTOS installed.'
echo './hephaistos.ps1 init --name "My Project" --mission "Describe the mission"'
