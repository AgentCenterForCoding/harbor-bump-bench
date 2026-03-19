# Fix Maven Compilation Failure: cactoos 0.35 -> 0.55.0

## Context

Project `java-api` (by zold-io) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`org.cactoos:cactoos` from `0.35` to `0.55.0` (minor update).

Reference PR: https://github.com/zold-io/java-api/pull/101

## Your Task

The source code is in `/java-api`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /java-api && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `0.55.0` has API changes vs `0.35`.
   Review the failing source files and update calls to match the new API.
   - Old API sources: https://repo1.maven.org/maven2/org/cactoos/cactoos/0.35/cactoos-0.35-sources.jar
   - New API sources: https://repo1.maven.org/maven2/org/cactoos/cactoos/0.55.0/cactoos-0.55.0-sources.jar

3. **Apply fixes** to the Java source files in `/java-api`.

4. **Verify:**
   ```bash
   cd /java-api && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
