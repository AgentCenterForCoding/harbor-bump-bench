# Stage 1: breaking project source
FROM ghcr.io/chains-project/breaking-updates:eb82573b99b6d9688e557d3490fa5d3e9512c99b-breaking AS breaking_src

FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends curl bash git procps openjdk-11-jdk-headless maven && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH
COPY --from=breaking_src /jooq-meta-postgres-flyway /jooq-meta-postgres-flyway
COPY --from=breaking_src /root/.m2 /root/.m2
WORKDIR /jooq-meta-postgres-flyway
