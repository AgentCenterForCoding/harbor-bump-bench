# Fix Maven Compilation Failure: struts2-core 2.3.37 -> 2.5.22

## Context

Project `guice` (by google) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`org.apache.struts:struts2-core` from `2.3.37` to `2.5.22` (minor update).

Reference PR: https://github.com/google/guice/pull/1551

## Your Task

The source code is in `/guice`. Fix all compilation errors so that `mvn compile` succeeds.
