#!/bin/bash
echo "=== Running mvn compile to verify fix ==="
cd /sorald
if mvn compile -B -q 2>&1; then
    echo "COMPILATION SUCCESS"
    echo "1.0" > /logs/verifier/reward.txt
else
    echo "COMPILATION FAILED"
    echo "0.0" > /logs/verifier/reward.txt
fi
