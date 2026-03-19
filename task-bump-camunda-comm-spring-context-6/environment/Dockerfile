# Stage 1: breaking project source
FROM ghcr.io/chains-project/breaking-updates:0ed34fa61c9e31bd4ebb7e4bf12ce792aec96091-breaking AS breaking_src

FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends curl bash git procps openjdk-11-jdk-headless maven && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH
COPY --from=breaking_src /camunda-platform-7-mockito /camunda-platform-7-mockito
COPY --from=breaking_src /root/.m2 /root/.m2
WORKDIR /camunda-platform-7-mockito
