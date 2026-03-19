# Fix Maven Compilation Failure: maven-surefire-common 3.0.0-M5 -> 3.0.0-M7

## Context

Project `flacoco` (by ASSERT-KTH) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`org.apache.maven.surefire:maven-surefire-common` from `3.0.0-M5` to `3.0.0-M7` (other update).

Reference PR: https://github.com/ASSERT-KTH/flacoco/pull/168

## Your Task

The source code is in `/flacoco`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /flacoco && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `3.0.0-M7` has API changes vs `3.0.0-M5`.
   Review the failing source files and update calls to match the new API.
   - Old API sources: https://repo1.maven.org/maven2/org/apache/maven/surefire/maven-surefire-common/3.0.0-M5/maven-surefire-common-3.0.0-M5-sources.jar
   - New API sources: https://repo1.maven.org/maven2/org/apache/maven/surefire/maven-surefire-common/3.0.0-M7/maven-surefire-common-3.0.0-M7-sources.jar

3. **Apply fixes** to the Java source files in `/flacoco`.

4. **Verify:**
   ```bash
   cd /flacoco && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
