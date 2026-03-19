# Fix Maven Compilation Failure: jakarta.mvc-api 1.1.0 -> 2.0.1

## Context

Project `jakartaee-mvc-sample` (by hantsy) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`jakarta.mvc:jakarta.mvc-api` from `1.1.0` to `2.0.1` (major update).

Reference PR: https://github.com/hantsy/jakartaee-mvc-sample/pull/140

## Your Task

The source code is in `/jakartaee-mvc-sample`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /jakartaee-mvc-sample && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `2.0.1` has API changes vs `1.1.0`.
   Review the failing source files and update calls to match the new API.
   - Old API sources: https://repo1.maven.org/maven2/jakarta/mvc/jakarta.mvc-api/1.1.0/jakarta.mvc-api-1.1.0-sources.jar
   - New API sources: https://repo1.maven.org/maven2/jakarta/mvc/jakarta.mvc-api/2.0.1/jakarta.mvc-api-2.0.1-sources.jar

3. **Apply fixes** to the Java source files in `/jakartaee-mvc-sample`.

4. **Verify:**
   ```bash
   cd /jakartaee-mvc-sample && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
