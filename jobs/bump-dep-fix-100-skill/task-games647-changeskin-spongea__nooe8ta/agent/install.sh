#!/bin/bash
set -euo pipefail

# Install curl if not available
if command -v apk &> /dev/null; then
    apk add --no-cache curl bash procps
elif command -v apt-get &> /dev/null; then
    apt-get update
    apt-get install -y curl procps
fi

# Install Claude Code using the official installer

curl -fsSL https://claude.ai/install.sh | bash


export PATH="$HOME/.local/bin:$PATH"
claude --version

# Inject skills from /logs/agent/skills/ into ~/.claude/skills/
# /logs/agent/ is mounted from the host trial_dir/agent/, pre-populated by the job runner.
if [ -d /logs/agent/skills ]; then
    mkdir -p ~/.claude/skills
    cp -r /logs/agent/skills/. ~/.claude/skills/
    echo "✅ Skills injected from /logs/agent/skills/ into ~/.claude/skills/"
    ls ~/.claude/skills/
fi