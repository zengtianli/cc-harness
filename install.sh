#!/usr/bin/env bash
# cc-harness install: symlink skills/commands/agents/harness.yaml to ~/.claude/
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"

echo "cc-harness install"
echo "repo:   $REPO_DIR"
echo "target: $CLAUDE_DIR"
echo ""

link_dir() {
  local name="$1"
  local src="$REPO_DIR/$name"
  local dst="$CLAUDE_DIR/$name"

  if [ -L "$dst" ]; then
    echo "  ✓ $name (already linked)"
  elif [ -d "$dst" ]; then
    echo "  ⚠ $name exists as directory, backing up to ${dst}.bak"
    mv "$dst" "${dst}.bak"
    ln -s "$src" "$dst"
    echo "  ✓ $name → $src"
  else
    ln -s "$src" "$dst"
    echo "  ✓ $name → $src"
  fi
}

link_file() {
  local name="$1"
  local src="$REPO_DIR/$name"
  local dst="$CLAUDE_DIR/$name"

  if [ -L "$dst" ]; then
    echo "  ✓ $name (already linked)"
  elif [ -f "$dst" ]; then
    echo "  ⚠ $name exists as file, backing up to ${dst}.bak"
    mv "$dst" "${dst}.bak"
    ln -s "$src" "$dst"
    echo "  ✓ $name → $src"
  else
    ln -s "$src" "$dst"
    echo "  ✓ $name → $src"
  fi
}

link_dir "skills"
link_dir "commands"
link_dir "agents"
link_file "harness.yaml"

echo ""
echo "Done. Verify: ls -la $CLAUDE_DIR/{skills,commands,agents,harness.yaml}"
