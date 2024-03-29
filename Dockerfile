#
#
#  Install stage
#
#
FROM python:3.10-slim AS compile-image
LABEL stage=compiler

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN \
    --mount=type=cache,target=/var/cache/apt \
    apt-get update; \
    apt-get install -yqq --no-install-recommends \
    build-essential gcc software-properties-common python3-psycopg2 libpq-dev python3-dev

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --default-timeout=100 --quiet --no-cache-dir -U --upgrade pip
RUN pip install --default-timeout=100 --quiet --no-cache-dir wheel

COPY requirements/base.txt .
COPY requirements/production.txt .

RUN \
    --mount=type=cache,target=/root/.cache \
    pip install --default-timeout=100 --quiet --no-cache-dir -r ./production.txt

RUN find /opt/venv -type f -name "*.pyc" -delete 2>/dev/null
RUN find /opt/venv -type f -name "*.pyo" -delete 2>/dev/null
RUN find /opt/venv -type d -name "test" -name "tests" -delete 2>/dev/null


#
#
#  Build for development
#
#
FROM python:3.10-slim AS build-local

WORKDIR /app/

COPY --from=compile-image /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN \
    --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install -yqq --no-install-recommends \
    supervisor wget nano curl python3-psycopg2

# Supervisor config
RUN mkdir -p /var/log/supervisor

ADD ./.supervisord/supervisord.conf /etc/supervisor/supervisord.conf
ADD ./.supervisord/api.conf /etc/supervisor/conf.d/api.conf
ADD ./.supervisord/celery_worker.conf /etc/supervisor/conf.d/celery_worker.conf
ADD ./.supervisord/celery_beat.conf /etc/supervisor/conf.d/celery_beat.conf
ADD ./.supervisord/celery_flower.conf /etc/supervisor/conf.d/celery_flower.conf

RUN mkdir -p /app/logs/

# Add required scripts
COPY ./scripts /app/scripts
RUN sed -i 's/\r$//g' /app/scripts/*
RUN chmod -R +x /app/scripts/*

# For security and image performance, directories will be hardcoded
COPY .envs /app/.envs
COPY apps /app/apps
COPY config /app/config
COPY static /app/static
COPY manage.py /app/manage.py


#
#
#  Build for production
#
#
FROM python:3.10-slim AS build-prod

WORKDIR /app/

COPY --from=compile-image /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN \
    --mount=type=cache,target=/var/cache/apt \
    apt-get update && \
    apt-get install -yqq --no-install-recommends \
    supervisor wget nano curl python3-psycopg2

# Supervisor config
RUN mkdir -p /var/log/supervisor

ADD ./.supervisord/supervisord.conf /etc/supervisor/supervisord.conf
ADD ./.supervisord/api.conf /etc/supervisor/conf.d/api.conf
ADD ./.supervisord/celery_worker.conf /etc/supervisor/conf.d/celery_worker.conf
ADD ./.supervisord/celery_beat.conf /etc/supervisor/conf.d/celery_beat.conf
ADD ./.supervisord/celery_flower.conf /etc/supervisor/conf.d/celery_flower.conf

RUN mkdir -p /app/logs/

# Add required scripts
COPY ./scripts /app/scripts
RUN sed -i 's/\r$//g' /app/scripts/*
RUN chmod -R +x /app/scripts/*

# For security and image performance, directories will be hardcoded
COPY .envs /app/.envs
COPY apps /app/apps
COPY config /app/config
COPY static /app/static
COPY manage.py /app/manage.py
