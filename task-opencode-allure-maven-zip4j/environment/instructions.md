# Fix Maven Compilation Failure: zip4j 1.3.2 -> 2.11.1

## Context

Project `allure-maven` (by allure-framework) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`net.lingala.zip4j:zip4j` from `1.3.2` to `2.11.1` (major update).

Reference PR: https://github.com/allure-framework/allure-maven/pull/241

## Your Task

The source code is in `/allure-maven`. Fix all compilation errors so that `mvn compile` succeeds.
