FROM ubuntu:16.04
LABEL maintainer "Vichara Wijetunga"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential libssl-dev libffi-dev libpq-dev