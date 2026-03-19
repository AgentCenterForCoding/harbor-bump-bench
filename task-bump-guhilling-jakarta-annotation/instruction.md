# Fix Maven Compilation Failure: jakarta.annotation-api 1.3.5 -> 2.0.0

## Context

Project `cdi-test` (by guhilling) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`jakarta.annotation:jakarta.annotation-api` from `1.3.5` to `2.0.0` (major update).

Reference PR: https://github.com/guhilling/cdi-test/pull/173

## Your Task

The source code is in `/cdi-test`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /cdi-test && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `2.0.0` has API changes vs `1.3.5`.
   Review the failing source files and update calls to match the new API.
   - Old API sources: https://repo1.maven.org/maven2/jakarta/annotation/jakarta.annotation-api/1.3.5/jakarta.annotation-api-1.3.5-sources.jar
   - New API sources: https://repo1.maven.org/maven2/jakarta/annotation/jakarta.annotation-api/2.0.0/jakarta.annotation-api-2.0.0-sources.jar

3. **Apply fixes** to the Java source files in `/cdi-test`.

4. **Verify:**
   ```bash
   cd /cdi-test && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
