# Fix Maven Compilation Failure: jaxb2-basics-runtime 0.13.1 -> 1.11.1

## Context

Project `billy` (by premium-minds) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`org.jvnet.jaxb2_commons:jaxb2-basics-runtime` from `0.13.1` to `1.11.1` (major update).

Reference PR: https://github.com/premium-minds/billy/pull/458

## Your Task

The source code is in `/billy`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /billy && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `1.11.1` has API changes vs `0.13.1`.
   Review the failing source files and update calls to match the new API.
   - Old API sources: https://repo1.maven.org/maven2/org/jvnet/jaxb2_commons/jaxb2-basics-runtime/0.13.1/jaxb2-basics-runtime-0.13.1-sources.jar
   - New API sources: https://repo1.maven.org/maven2/org/jvnet/jaxb2_commons/jaxb2-basics-runtime/1.11.1/jaxb2-basics-runtime-1.11.1-sources.jar

3. **Apply fixes** to the Java source files in `/billy`.

4. **Verify:**
   ```bash
   cd /billy && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
