FROM mcr.microsoft.com/devcontainers/python:3.11

RUN apt-get update && \
    apt-get install -y cmake nodejs npm && \
    npm install -g emscripten

RUN pip install --upgrade pip && \
    pip install pygbag