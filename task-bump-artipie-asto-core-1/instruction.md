# Fix Maven Compilation Failure: asto-core v1.13.0 -> v1.15.3

## Context

Project `http` (by artipie) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`com.artipie:asto-core` from `v1.13.0` to `v1.15.3` (other update).

Reference PR: https://github.com/artipie/http/pull/508

## Your Task

The source code is in `/http`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /http && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `v1.15.3` has API changes vs `v1.13.0`.
   Review the failing source files and update calls to match the new API.
   - Old API sources: https://repo1.maven.org/maven2/com/artipie/asto-core/v1.13.0/asto-core-v1.13.0-sources.jar
   - New API sources: https://repo1.maven.org/maven2/com/artipie/asto-core/v1.15.3/asto-core-v1.15.3-sources.jar

3. **Apply fixes** to the Java source files in `/http`.

4. **Verify:**
   ```bash
   cd /http && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
