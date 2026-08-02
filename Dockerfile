FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates \
    && rm -rf /var/lib/apt-get/lists/*

WORKDIR /app

RUN pip install --no-cache-dir hermes-agent

COPY . .

CMD ["python", "main.py"]
