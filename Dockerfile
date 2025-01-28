FROM python:3.12-slim-bullseye AS prod
RUN apt-get update && apt-get install -y \
  gcc \
  && rm -rf /var/lib/apt/lists/*


RUN pip install poetry==1.8.5

# Configuring poetry
RUN poetry config virtualenvs.create false
RUN poetry config cache-dir /tmp/poetry_cache

# Copying requirements of a project
COPY pyproject.toml poetry.lock /app/
WORKDIR /app

# Installing requirements
RUN --mount=type=cache,target=/tmp/poetry_cache poetry install --only main
# Removing gcc
RUN apt-get purge -y \
  gcc \
  && rm -rf /var/lib/apt/lists/*

# Copying actuall application
COPY . /app
RUN --mount=type=cache,target=/tmp/poetry_cache poetry install --only main

RUN ["prisma", "generate", "--schema", "app/prisma/schema.prisma"]

CMD ["/usr/local/bin/python", "-m", "app"]

FROM prod AS dev

RUN --mount=type=cache,target=/tmp/poetry_cache poetry install

