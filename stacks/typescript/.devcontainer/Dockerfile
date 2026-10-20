# Dev container image for the TypeScript stack: Ubuntu and just. Node.js comes from the node
# feature (devcontainer.json) and pnpm from corepack, at the version pinned in package.json.
# postCreateCommand points pnpm's store to the home folder: by default pnpm would put it at the root
# of the project's mount, inside the folder shared with the host.
FROM mcr.microsoft.com/devcontainers/base:ubuntu

RUN apt-get update \
    && apt-get install -y --no-install-recommends just \
    && rm -rf /var/lib/apt/lists/*
