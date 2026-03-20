# Fix Maven Compilation Failure: hibernate-validator 5.4.3.Final -> 8.0.1.Final

## Context

Project `nem` (by NemProject) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`org.hibernate:hibernate-validator` from `5.4.3.Final` to `8.0.1.Final` (other update).

Reference PR: https://github.com/NemProject/nem/pull/304

## Your Task

The source code is in `/nem`. Fix all compilation errors so that `mvn compile` succeeds.
