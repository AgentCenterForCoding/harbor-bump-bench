# Fix Maven Compilation Failure: zip4j 1.3.2 -> 2.10.0

## Context

Project `allure-maven` (by allure-framework) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`net.lingala.zip4j:zip4j` from `1.3.2` to `2.10.0` (major update).

Reference PR: https://github.com/allure-framework/allure-maven/pull/230

## Your Task

The source code is in `/allure-maven`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /allure-maven && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `2.10.0` has API changes vs `1.3.2`.
   Review the failing source files and update calls to match the new API.
   - Old API sources: https://repo1.maven.org/maven2/net/lingala/zip4j/zip4j/1.3.2/zip4j-1.3.2-sources.jar
   - New API sources: https://repo1.maven.org/maven2/net/lingala/zip4j/zip4j/2.10.0/zip4j-2.10.0-sources.jar

3. **Apply fixes** to the Java source files in `/allure-maven`.

4. **Verify:**
   ```bash
   cd /allure-maven && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
