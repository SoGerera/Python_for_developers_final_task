FROM python:3.13-slim

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./

RUN pip install poetry

RUN poetry config virtualenvs.create false

COPY src/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && \
    sed -i 's/\r$//' /entrypoint.sh 2>/dev/null || sed -i '' 's/\r$//' /entrypoint.sh 2>/dev/null || true

COPY . .

RUN poetry install --no-root

ENV PYTHONPATH=/app/src

ENTRYPOINT ["/entrypoint.sh"]