# Fix Maven Compilation Failure: jakarta.validation-api 2.0.2 -> 3.0.2

## Context

Project `wicket-crudifier` (by premium-minds) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`jakarta.validation:jakarta.validation-api` from `2.0.2` to `3.0.2` (major update).

Reference PR: https://github.com/premium-minds/wicket-crudifier/pull/91

## Your Task

The source code is in `/wicket-crudifier`. Fix all compilation errors so that `mvn compile` succeeds.
