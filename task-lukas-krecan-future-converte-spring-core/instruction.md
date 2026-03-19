# Fix Maven Compilation Failure: spring-core 5.3.19 -> 6.0.4

## Context

Project `future-converter` (by lukas-krecan) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`org.springframework:spring-core` from `5.3.19` to `6.0.4` (major update).

Reference PR: https://github.com/lukas-krecan/future-converter/pull/85

## Your Task

The source code is in `/future-converter`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /future-converter && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `6.0.4` has API changes vs `5.3.19`.
   Review the failing source files and update calls to match the new API.
   - Old API sources: https://repo1.maven.org/maven2/org/springframework/spring-core/5.3.19/spring-core-5.3.19-sources.jar
   - New API sources: https://repo1.maven.org/maven2/org/springframework/spring-core/6.0.4/spring-core-6.0.4-sources.jar

3. **Apply fixes** to the Java source files in `/future-converter`.

4. **Verify:**
   ```bash
   cd /future-converter && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
