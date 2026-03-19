# Fix Maven Compilation Failure: spring-context 5.3.23 -> 6.0.10

## Context

Project `camunda-platform-7-mockito` (by camunda-community-hub) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`org.springframework:spring-context` from `5.3.23` to `6.0.10` (major update).

Reference PR: https://github.com/camunda-community-hub/camunda-platform-7-mockito/pull/320

## Your Task

The source code is in `/camunda-platform-7-mockito`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /camunda-platform-7-mockito && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `6.0.10` has API changes vs `5.3.23`.
   Review the failing source files and update calls to match the new API.
   - Old API sources: https://repo1.maven.org/maven2/org/springframework/spring-context/5.3.23/spring-context-5.3.23-sources.jar
   - New API sources: https://repo1.maven.org/maven2/org/springframework/spring-context/6.0.10/spring-context-6.0.10-sources.jar

3. **Apply fixes** to the Java source files in `/camunda-platform-7-mockito`.

4. **Verify:**
   ```bash
   cd /camunda-platform-7-mockito && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
