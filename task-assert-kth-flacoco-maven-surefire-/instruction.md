# Fix Maven Compilation Failure: maven-surefire-common 3.0.0-M5 -> 3.0.0-M7

## Context

Project `flacoco` (by ASSERT-KTH) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`org.apache.maven.surefire:maven-surefire-common` from `3.0.0-M5` to `3.0.0-M7` (other update).

Reference PR: https://github.com/ASSERT-KTH/flacoco/pull/168

## Your Task

The source code is in `/flacoco`. Fix all compilation errors so that `mvn compile` succeeds.
