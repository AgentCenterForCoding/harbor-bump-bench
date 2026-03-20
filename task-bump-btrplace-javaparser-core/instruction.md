# Fix Maven Compilation Failure: javaparser-core 3.18.0 -> 3.24.0

## Context

Project `scheduler` (by btrplace) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`com.github.javaparser:javaparser-core` from `3.18.0` to `3.24.0` (minor update).

Reference PR: https://github.com/btrplace/scheduler/pull/347

## Your Task

The source code is in `/scheduler`. Fix all compilation errors so that `mvn compile` succeeds.
