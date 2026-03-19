#!/bin/bash
set -e
echo "=== Applying fix: snakeyaml 1.17 -> 1.31 API change ==="

FILE="/polyglot-maven/polyglot-yaml/src/main/java/org/sonatype/maven/polyglot/yaml/ModelRepresenter.java"

# snakeyaml 1.31: Representer.getProperties() no longer throws IntrospectionException
# Remove 'throws IntrospectionException' from overriding methods
sed -i 's/ throws IntrospectionException//' "$FILE"

# Remove the now-unused import
sed -i '/import java.beans.IntrospectionException;/d' "$FILE"

echo "Fix applied to ModelRepresenter.java"
echo ""

echo "=== Verifying fix (excluding unrelated polyglot-ruby module) ==="
cd /polyglot-maven
mvn compile -B -q --projects '!polyglot-ruby' 2>&1

echo "=== COMPILATION SUCCESS ==="
