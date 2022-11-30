FROM ubuntu:rolling as base

RUN apt-get update && \
    apt-get install -yqq tox firefox

ENV PATH=${PATH}:/root/.local:/root/.local/bin

COPY . .

RUN tox
