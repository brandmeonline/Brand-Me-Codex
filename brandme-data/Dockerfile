# Copyright (c) Brand.Me, Inc. All rights reserved.
# Base container for running migrations and seed jobs.

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY migrations ./migrations
COPY seed ./seed

RUN pip install --no-cache-dir psycopg2-binary==2.9.9

CMD ["sleep", "infinity"]
