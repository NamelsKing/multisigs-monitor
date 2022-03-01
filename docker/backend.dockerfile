FROM python:3.9.8-slim AS base

WORKDIR /app

ENV PYTHONPATH "${PYTHONPATH}:/app"

RUN apt-get update && \
    apt-get install -y tzdata locales && \
    ln -sf /usr/share/zoneinfo/UTC /etc/localtime && \
    locale-gen en_US.UTF-8 ru_RU.UTF-8 ru_UA.UTF-8 && \
    apt-get install --no-install-recommends --no-install-suggests -y \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y gcc make libffi-dev g++ wget

COPY requirements /app/requirements

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements/backend.txt --no-deps --default-timeout=100


FROM base AS dev

RUN apt-get install -y wget xz-utils

RUN wget -q -O /tmp/watchexec.tar.xz \
        https://github.com/watchexec/watchexec/releases/download/1.12.0/watchexec-1.12.0-x86_64-unknown-linux-gnu.tar.xz && \
        cd /usr/local/bin && \
        tar -xf /tmp/watchexec.tar.xz --strip 1 --wildcards 'watchexec-*/watchexec' && \
        rm /tmp/watchexec.tar.xz

RUN pip install pip-tools==6.4.0
RUN mkdir -p /.cache/pip-tools && chmod -R 777 /.cache/pip-tools

FROM base AS checks

ENV MYPYPATH "${MYPYPATH}:/app"
RUN pip3 install -r requirements/checks.txt --no-deps --no-cache-dir

FROM base AS real

ARG CONFIG_PATH_INN
ARG DISCORD_BOT_TOKEN_INN

ENV CONFIG_PATH ${CONFIG_PATH_INN}
ENV DISCORD_BOT_TOKEN ${DISCORD_BOT_TOKEN_INN}

COPY config /app/config
COPY monitor /app/monitor

CMD python3 -m monitor
