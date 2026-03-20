# Fix Maven Compilation Failure: spring-cloud-stream 3.0.7.RELEASE -> 4.0.0

## Context

Project `log-record` (by qqxx6661) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`org.springframework.cloud:spring-cloud-stream` from `3.0.7.RELEASE` to `4.0.0` (other update).

Reference PR: https://github.com/qqxx6661/log-record/pull/45

## Your Task

The source code is in `/log-record`. Fix all compilation errors so that `mvn compile` succeeds.
