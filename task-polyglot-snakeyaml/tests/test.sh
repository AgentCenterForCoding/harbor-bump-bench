#!/bin/bash
echo "=== Running mvn compile to verify fix ==="
cd /polyglot-maven
# Exclude polyglot-ruby: has pre-existing rubygems dependency issue unrelated to snakeyaml
if mvn compile -B -q --projects '!polyglot-ruby' 2>&1; then
    echo "COMPILATION SUCCESS"
    echo "1.0" > /logs/verifier/reward.txt
else
    echo "COMPILATION FAILED"
    echo "0.0" > /logs/verifier/reward.txt
fi
