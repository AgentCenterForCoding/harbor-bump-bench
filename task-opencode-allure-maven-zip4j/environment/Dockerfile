# Stage 1: breaking project source (Alpine-based)
FROM ghcr.io/chains-project/breaking-updates:16ae40b1e17e14ee3ae20ac211647e47399a01a9-breaking AS breaking_src

FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends curl bash git procps openjdk-11-jdk-headless maven && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH
COPY --from=breaking_src /allure-maven /allure-maven
COPY --from=breaking_src /root/.m2 /root/.m2

# Clone open-skills repository and copy java-dep-fix skill
RUN git clone --depth 1 https://github.com/AgentCenterForCoding/open-skills.git /tmp/open-skills && \
    mkdir -p /allure-maven/.opencode/skills/java-dep-fix && \
    cp /tmp/open-skills/java-dep-fix/SKILL.md /allure-maven/.opencode/skills/java-dep-fix/SKILL.md && \
    rm -rf /tmp/open-skills

# Copy instructions.md to opencode directory
COPY instructions.md /allure-maven/.opencode/instructions.md

# Configure opencode to use dashscope anthropic-compatible API
RUN mkdir -p /root/.config/opencode && echo '{ \
  "$schema": "https://opencode.ai/config.json", \
  "provider": { \
    "anthropic": { \
      "npm": "@ai-sdk/anthropic", \
      "name": "Anthropic (DashScope)", \
      "options": { \
        "baseURL": "https://coding.dashscope.aliyuncs.com/apps/anthropic/v1" \
      }, \
      "models": { \
        "qwen3.5-plus": { "name": "Qwen3.5 Plus" } \
      } \
    } \
  } \
}' > /root/.config/opencode/opencode.json

WORKDIR /allure-maven
