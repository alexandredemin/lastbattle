FROM mcr.microsoft.com/devcontainers/python:3.11

RUN apt-get update && \
    apt-get install -y cmake nodejs npm git-lfs && \
    npm install -g emscripten && \
    git lfs install

RUN pip install --upgrade pip && \
    pip install pygbag