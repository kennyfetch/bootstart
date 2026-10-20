# Dev container image for the Python stack: Ubuntu, just and uv. uv then installs the Python
# version pinned in .python-version, exactly as on the host and in CI. Node.js comes from the node
# feature (devcontainer.json): Claude Code needs it, and Pyright uses it instead of downloading one.
# The node feature also brings Ubuntu's python3-minimal, which lacks parts of the standard library:
# UV_PYTHON_PREFERENCE=only-managed (devcontainer.json) keeps uv on its own complete Python.
FROM mcr.microsoft.com/devcontainers/base:ubuntu

RUN apt-get update \
    && apt-get install -y --no-install-recommends just \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/
