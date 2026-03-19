# Stage 1: breaking project source
FROM ghcr.io/chains-project/breaking-updates:fe15d2a6e52b049f6c9e7cc123a5402047a1f01a-breaking AS breaking_src

FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends curl bash git procps openjdk-11-jdk-headless maven && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH
COPY --from=breaking_src /billy /billy
COPY --from=breaking_src /root/.m2 /root/.m2
WORKDIR /billy
