#!/bin/bash
# Harbor verifier: reward must be written to /logs/verifier/reward.txt
# 1.0 = success, 0.0 = failure
set -uo pipefail

REWARD_FILE="/logs/verifier/reward.txt"
mkdir -p /logs/verifier

echo "=== Running mvn compile to verify fix ==="
cd /IDS-Messaging-Services

if mvn compile -B -q 2>&1; then
    echo "COMPILATION SUCCESS"
    echo "1.0" > "$REWARD_FILE"
    exit 0
else
    echo "COMPILATION FAILED"
    echo "0.0" > "$REWARD_FILE"
    exit 1
fi
