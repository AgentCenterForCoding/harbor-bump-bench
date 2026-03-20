# Fix Maven Compilation Failure: acceptance-test-harness 5588.vd13b_52985008 -> 5623.v3e1d330b_89e0

## Context

Project `code-coverage-api-plugin` (by jenkinsci) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`org.jenkins-ci:acceptance-test-harness` from `5588.vd13b_52985008` to `5623.v3e1d330b_89e0` (other update).

Reference PR: https://github.com/jenkinsci/code-coverage-api-plugin/pull/707

## Your Task

The source code is in `/code-coverage-api-plugin`. Fix all compilation errors so that `mvn compile` succeeds.
