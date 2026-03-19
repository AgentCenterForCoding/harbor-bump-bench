# Fix Maven Compilation Failure: jetty-server 8.1.11.v20130520 -> 9.4.41.v20210516

## Context

Project `jadler` (by jadler-mocking) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`org.eclipse.jetty:jetty-server` from `8.1.11.v20130520` to `9.4.41.v20210516` (other update).

Reference PR: https://github.com/jadler-mocking/jadler/pull/160

## Your Task

The source code is in `/jadler`. Fix all compilation errors so that `mvn compile` succeeds.

## Steps

1. **Identify errors:**
   ```bash
   cd /jadler && mvn compile -B 2>&1 | grep -E "^\[ERROR\]" | head -60
   ```

2. **Understand breaking changes:** The new version `9.4.41.v20210516` has API changes vs `8.1.11.v20130520`.
   Review the failing source files and update calls to match the new API.
   - Old API sources: https://repo1.maven.org/maven2/org/eclipse/jetty/jetty-server/8.1.11.v20130520/jetty-server-8.1.11.v20130520-sources.jar
   - New API sources: https://repo1.maven.org/maven2/org/eclipse/jetty/jetty-server/9.4.41.v20210516/jetty-server-9.4.41.v20210516-sources.jar

3. **Apply fixes** to the Java source files in `/jadler`.

4. **Verify:**
   ```bash
   cd /jadler && mvn compile -B -q
   ```

## Success Criteria

`mvn compile` exits with **code 0** (no compilation errors).
