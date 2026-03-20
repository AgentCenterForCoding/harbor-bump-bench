# Fix Maven Compilation Failure: jakarta.annotation-api 1.3.5 -> 2.0.0

## Context

Project `cdi-test` (by guhilling) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`jakarta.annotation:jakarta.annotation-api` from `1.3.5` to `2.0.0` (major update).

Reference PR: https://github.com/guhilling/cdi-test/pull/173

## Your Task

The source code is in `/cdi-test`. Fix all compilation errors so that `mvn compile` succeeds.
