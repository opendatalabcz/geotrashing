FROM ubuntu:20.04

RUN  useradd -u 999 app_user && apt-get update && apt-get upgrade -y && apt-get install -y gunicorn build-essential make python3.8-venv python3-pip
COPY requirements.txt Makefile /srv/
WORKDIR /srv
RUN make setup
COPY . /srv

ENV HOST_IP=${HOST_IP}
ENV HOST_PORT=${HOST_PORT}

EXPOSE ${HOST_PORT}
USER app_user
HEALTHCHECK CMD curl --fail ${HOST_IP}:${HOST_PORT}
# Entrypoint
CMD ["make", "deploy"]
