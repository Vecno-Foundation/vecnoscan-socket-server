FROM python:3.10-alpine

ARG REPO_DIR

EXPOSE 8000

ENV VECNOD_HOSTS_1=seed.vecnoscan.org:7110
ENV SQL_URI=postgresql+asyncpg://postgres:password@postgresql:5432/postgres
ARG version
ENV VERSION=$version

RUN apk --no-cache add \
  git \
  gcc \
  libc-dev \
  build-base \
  linux-headers \
  libpq-dev \
  dumb-init

RUN pip install \
  pipenv

RUN addgroup -S -g 55747 api \
  && adduser -h /app -S -D -g '' -G api -u 55747 api 

WORKDIR /app
USER api

COPY --chown=api:api . /app

RUN pipenv install --deploy

ENTRYPOINT ["/usr/bin/dumb-init", "--"]

CMD pipenv run gunicorn -b 0.0.0.0:8000 -w 1 -k uvicorn.workers.UvicornWorker main:app --timeout 120
