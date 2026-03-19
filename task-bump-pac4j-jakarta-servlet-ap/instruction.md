# Fix Maven Compilation Failure: jakarta.servlet-api 4.0.4 -> 6.0.0

## Context

Project `dropwizard-pac4j` (by pac4j) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`jakarta.servlet:jakarta.servlet-api` from `4.0.4` to `6.0.0` (major update).

Reference PR: https://github.com/pac4j/dropwizard-pac4j/pull/292

## Your Task

The source code is in `/dropwizard-pac4j`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /dropwizard-pac4j && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `6.0.0` has API changes vs `4.0.4`.
   Review the failing source files and update calls to match the new API.
   - Old API sources: https://repo1.maven.org/maven2/jakarta/servlet/jakarta.servlet-api/4.0.4/jakarta.servlet-api-4.0.4-sources.jar
   - New API sources: https://repo1.maven.org/maven2/jakarta/servlet/jakarta.servlet-api/6.0.0/jakarta.servlet-api-6.0.0-sources.jar

3. **Apply fixes** to the Java source files in `/dropwizard-pac4j`.

4. **Verify:**
   ```bash
   cd /dropwizard-pac4j && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
