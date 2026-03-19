# Fix Maven Compilation Failure: jakarta.validation-api 2.0.2 -> 3.0.1

## Context

Project `wicket-crudifier` (by premium-minds) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`jakarta.validation:jakarta.validation-api` from `2.0.2` to `3.0.1` (major update).

Reference PR: https://github.com/premium-minds/wicket-crudifier/pull/93

## Your Task

The source code is in `/wicket-crudifier`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /wicket-crudifier && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `3.0.1` has API changes vs `2.0.2`.
   Review the failing source files and update calls to match the new API.
   - Old API sources: https://repo1.maven.org/maven2/jakarta/validation/jakarta.validation-api/2.0.2/jakarta.validation-api-2.0.2-sources.jar
   - New API sources: https://repo1.maven.org/maven2/jakarta/validation/jakarta.validation-api/3.0.1/jakarta.validation-api-3.0.1-sources.jar

3. **Apply fixes** to the Java source files in `/wicket-crudifier`.

4. **Verify:**
   ```bash
   cd /wicket-crudifier && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
