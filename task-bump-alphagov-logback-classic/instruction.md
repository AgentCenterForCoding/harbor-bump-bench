# Fix Maven Compilation Failure: logback-classic 1.2.11 -> 1.4.1

## Context

Project `pay-adminusers` (by alphagov) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`ch.qos.logback:logback-classic` from `1.2.11` to `1.4.1` (minor update).

Reference PR: https://github.com/alphagov/pay-adminusers/pull/1594

## Your Task

The source code is in `/pay-adminusers`. Fix all compilation errors so that `mvn compile` succeeds.
