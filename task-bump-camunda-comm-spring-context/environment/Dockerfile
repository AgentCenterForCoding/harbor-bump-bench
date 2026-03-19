# Stage 1: breaking project source
FROM ghcr.io/chains-project/breaking-updates:c5905f7220e1129a0448715ee5d0e61ee5ac31e1-breaking AS breaking_src

FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends curl bash git procps openjdk-11-jdk-headless maven && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH
COPY --from=breaking_src /camunda-platform-7-mockito /camunda-platform-7-mockito
COPY --from=breaking_src /root/.m2 /root/.m2
WORKDIR /camunda-platform-7-mockito
