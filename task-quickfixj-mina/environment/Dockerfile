# Stage 1: breaking project source (Alpine-based)
FROM ghcr.io/chains-project/breaking-updates:00a7cc31784ac4a9cc27d506a73ae589d6df36d6-breaking AS breaking_src

# Stage 2: Ubuntu environment (glibc-based, compatible with Claude Code binary)
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends     curl bash git procps     openjdk-11-jdk-headless     maven     && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Copy project files and pre-populated Maven local cache
COPY --from=breaking_src /quickfixj /quickfixj
COPY --from=breaking_src /root/.m2 /root/.m2

WORKDIR /quickfixj
