FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md LICENSE /app/
COPY src /app/src

RUN pip install --no-cache-dir -e .

VOLUME ["/watch", "/output", "/config"]
EXPOSE 8000

CMD ["discoball", "watch"]
