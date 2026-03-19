#!/bin/bash
set -e
echo "=== Applying fix: libthrift 0.12.0 -> 0.16.0 API change ==="

FILE="/singer/singer-commons/src/main/java/com/pinterest/singer/loggingaudit/client/AuditEventKafkaSender.java"

# libthrift 0.16.0: TSerializer() constructor now throws TTransportException
# Fix: replace inline field initializer with lazy instance-initializer block

# Step 1: Replace the field declaration (remove inline new TSerializer())
sed -i 's/private TSerializer serializer = new TSerializer();/private TSerializer serializer;/' "$FILE"

# Step 2: Insert instance initializer block right after the field declaration using awk
awk '
/private TSerializer serializer;/ {
    print $0
    print "  {"
    print "    try {"
    print "      this.serializer = new TSerializer();"
    print "    } catch (org.apache.thrift.transport.TTransportException e) {"
    print "      throw new RuntimeException(\"Failed to initialize TSerializer\", e);"
    print "    }"
    print "  }"
    next
}
{ print }
' "$FILE" > /tmp/AuditEventKafkaSender_fixed.java && mv /tmp/AuditEventKafkaSender_fixed.java "$FILE"

echo "Fix applied to AuditEventKafkaSender.java"
echo ""

echo "=== Verifying fix ==="
cd /singer
mvn compile -B -q 2>&1
echo "=== COMPILATION SUCCESS ==="
