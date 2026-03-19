# Stage 1: breaking project source (Alpine-based)
FROM ghcr.io/chains-project/breaking-updates:5b90c67ef2d2ebb296534ea2ce8d8955cf6854c7-breaking AS breaking_src

FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends curl bash git procps openjdk-11-jdk-headless maven && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH
COPY --from=breaking_src /LPVS /LPVS
COPY --from=breaking_src /root/.m2 /root/.m2
WORKDIR /LPVS
