# Fix Maven Compilation Failure: pitest-entry 1.9.11 -> 1.10.0

## Context

Project `pitest-mutation-testing-elements-plugin` (by Wmaarts) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`org.pitest:pitest-entry` from `1.9.11` to `1.10.0` (minor update).

Reference PR: https://github.com/Wmaarts/pitest-mutation-testing-elements-plugin/pull/146

## Your Task

The source code is in `/pitest-mutation-testing-elements-plugin`. Fix all compilation errors so that `mvn compile` succeeds.
