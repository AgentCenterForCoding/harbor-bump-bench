# Fix Maven Compilation Failure: maven-dependency-tree 3.1.1 -> 3.2.0

## Context

Project `license-maven-plugin` (by mathieucarbou) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`org.apache.maven.shared:maven-dependency-tree` from `3.1.1` to `3.2.0` (minor update).

Reference PR: https://github.com/mathieucarbou/license-maven-plugin/pull/410

## Your Task

The source code is in `/license-maven-plugin`. Fix all compilation errors so that `mvn compile` succeeds.
