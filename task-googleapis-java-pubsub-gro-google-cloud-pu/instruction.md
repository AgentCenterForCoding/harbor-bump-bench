# Fix Maven Compilation Failure: google-cloud-pubsublite 0.6.0 -> 1.6.3

## Context

Project `java-pubsub-group-kafka-connector` (by googleapis) has a **COMPILATION_FAILURE** after a dependency upgrade bot bumped
`com.google.cloud:google-cloud-pubsublite` from `0.6.0` to `1.6.3` (major update).

Reference PR: https://github.com/googleapis/java-pubsub-group-kafka-connector/pull/41

## Your Task

The source code is in `/java-pubsub-group-kafka-connector`. Fix all compilation errors so that `mvn compile` succeeds.
