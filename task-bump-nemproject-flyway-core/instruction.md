# Fix Maven Compilation Failure: flyway-core 3.2.1 -> 9.21.1

## Context

Project `nem` (by NemProject) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`org.flywaydb:flyway-core` from `3.2.1` to `9.21.1` (major update).

Reference PR: https://github.com/NemProject/nem/pull/318

## Your Task

The source code is in `/nem`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /nem && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `9.21.1` has API changes vs `3.2.1`.
   Review the failing source files and update calls to match the new API.
   - Old API sources: https://repo1.maven.org/maven2/org/flywaydb/flyway-core/3.2.1/flyway-core-3.2.1-sources.jar
   - New API sources: https://repo1.maven.org/maven2/org/flywaydb/flyway-core/9.21.1/flyway-core-9.21.1-sources.jar

3. **Apply fixes** to the Java source files in `/nem`.

4. **Verify:**
   ```bash
   cd /nem && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
