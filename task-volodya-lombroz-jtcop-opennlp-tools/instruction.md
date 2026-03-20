# Fix Maven Compilation Failure: opennlp-tools 2.2.0 -> 2.3.0

## Context

Project `jtcop` (by volodya-lombrozo) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`org.apache.opennlp:opennlp-tools` from `2.2.0` to `2.3.0` (minor update).

Reference PR: https://github.com/volodya-lombrozo/jtcop/pull/258

## Your Task

The source code is in `/jtcop`. Fix all compilation errors so that `mvn compile` succeeds.
