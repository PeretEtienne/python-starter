FROM python:3.12-slim-bullseye AS prod

WORKDIR /app

RUN apt-get update && apt-get install -y gcc \
  && pip install poetry==1.8.5 \
  && poetry config virtualenvs.create false \
  && poetry config cache-dir /tmp/poetry_cache \
  && apt-get purge -y gcc \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock /app/

RUN --mount=type=cache,target=/tmp/poetry_cache poetry install --only main --no-root \
  && rm -rf /root/.cache/pip

COPY . /app

CMD ["python", "-m", "app"]
