# Build from the repository root:
#   docker build --platform linux/amd64 -f benchmarks/reviewbench/Dockerfile -t ponderly-review:dev .
FROM node:22-slim

ARG CLAUDE_CODE_VERSION=2.1.312

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates python3 \
    && rm -rf /var/lib/apt/lists/*

# ReviewBench mounts /work/repo owned by another uid; git refuses it without this.
RUN git config --system --add safe.directory '*'

RUN npm install -g "@anthropic-ai/claude-code@${CLAUDE_CODE_VERSION}" \
    && npm cache clean --force

COPY plugins/ponderly /opt/ponderly
COPY benchmarks/reviewbench/agent /agent

# No USER line: the entrypoint runs as root so it can write /work/out whatever the
# mount's owner, and the adapter starts Claude Code as reviewer, because Claude Code
# refuses bypassPermissions as root and writes under ~/.claude.
RUN useradd --create-home --shell /bin/bash reviewer
WORKDIR /home/reviewer

ENTRYPOINT ["python3", "-I", "/agent/agent.py"]
