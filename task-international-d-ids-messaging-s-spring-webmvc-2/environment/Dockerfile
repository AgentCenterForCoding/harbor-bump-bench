# Stage 1: breaking project source (Alpine-based)
FROM ghcr.io/chains-project/breaking-updates:f5dbb3021aa96afc60b38d2b0b01873d3a6f16bd-breaking AS breaking_src

FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends curl bash git procps openjdk-11-jdk-headless maven && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH
COPY --from=breaking_src /IDS-Messaging-Services /IDS-Messaging-Services
COPY --from=breaking_src /root/.m2 /root/.m2
WORKDIR /IDS-Messaging-Services
