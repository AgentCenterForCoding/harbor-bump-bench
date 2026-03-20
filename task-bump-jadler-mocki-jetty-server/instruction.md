# Fix Maven Compilation Failure: jetty-server 8.1.11.v20130520 -> 9.4.41.v20210516

## Context

Project `jadler` (by jadler-mocking) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`org.eclipse.jetty:jetty-server` from `8.1.11.v20130520` to `9.4.41.v20210516` (other update).

Reference PR: https://github.com/jadler-mocking/jadler/pull/160

## Your Task

The source code is in `/jadler`. Fix all compilation errors so that `mvn compile` succeeds.
