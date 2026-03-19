# Fix Maven Compilation Failure: spring-core 5.3.24 -> 6.0.5

## Context

Project `IDS-Messaging-Services` (by International-Data-Spaces-Association) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`org.springframework:spring-core` from `5.3.24` to `6.0.5` (major update).

Reference PR: https://github.com/International-Data-Spaces-Association/IDS-Messaging-Services/pull/704

## Your Task

The source code is in `/IDS-Messaging-Services`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /IDS-Messaging-Services && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `6.0.5` has API changes vs `5.3.24`.
   Review the failing source files and update calls to match the new API.
   - Old API sources: https://repo1.maven.org/maven2/org/springframework/spring-core/5.3.24/spring-core-5.3.24-sources.jar
   - New API sources: https://repo1.maven.org/maven2/org/springframework/spring-core/6.0.5/spring-core-6.0.5-sources.jar

3. **Apply fixes** to the Java source files in `/IDS-Messaging-Services`.

4. **Verify:**
   ```bash
   cd /IDS-Messaging-Services && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
