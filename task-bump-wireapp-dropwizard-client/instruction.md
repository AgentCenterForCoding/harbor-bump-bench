# Fix Maven Compilation Failure: dropwizard-client 2.1.5 -> 4.0.0

## Context

Project `lithium` (by wireapp) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`io.dropwizard:dropwizard-client` from `2.1.5` to `4.0.0` (major update).

Reference PR: https://github.com/wireapp/lithium/pull/98

## Your Task

The source code is in `/lithium`. Fix all compilation errors so that `mvn compile` succeeds.
