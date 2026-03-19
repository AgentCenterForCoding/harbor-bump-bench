# Fix Maven Compilation Failure: javaparser-core 3.18.0 -> 3.24.0

## Context

Project `scheduler` (by btrplace) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`com.github.javaparser:javaparser-core` from `3.18.0` to `3.24.0` (minor update).

Reference PR: https://github.com/btrplace/scheduler/pull/347

## Your Task

The source code is in `/scheduler`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /scheduler && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `3.24.0` has API changes vs `3.18.0`.
   Review the failing source files and update calls to match the new API.
   - Old API sources: https://repo1.maven.org/maven2/com/github/javaparser/javaparser-core/3.18.0/javaparser-core-3.18.0-sources.jar
   - New API sources: https://repo1.maven.org/maven2/com/github/javaparser/javaparser-core/3.24.0/javaparser-core-3.24.0-sources.jar

3. **Apply fixes** to the Java source files in `/scheduler`.

4. **Verify:**
   ```bash
   cd /scheduler && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
