# Fix Maven Compilation Failure: jasperreports 6.18.1 -> 6.19.1

## Context

Project `biapi` (by xdev-software) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`net.sf.jasperreports:jasperreports` from `6.18.1` to `6.19.1` (minor update).

Reference PR: https://github.com/xdev-software/biapi/pull/69

## Your Task

The source code is in `/biapi`. Fix all compilation errors so that `mvn compile` succeeds.
