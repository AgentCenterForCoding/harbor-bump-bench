# Stage 1: breaking project source
FROM ghcr.io/chains-project/breaking-updates:471d07e01cd0c79dc9bed5344ed46418f4c078a2-breaking AS breaking_src

FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends curl bash git procps openjdk-11-jdk-headless maven && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH
COPY --from=breaking_src /google-cloud-java /google-cloud-java
COPY --from=breaking_src /root/.m2 /root/.m2
WORKDIR /google-cloud-java
