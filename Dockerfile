FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x /app/docker-entrypoint.sh

ENV PORT=5100
ENV API_BASE_URL=http://127.0.0.1:5000/api
ENV BACKEND_HEALTH_URL=http://127.0.0.1:5000/healthz

EXPOSE 5100

CMD ["/app/docker-entrypoint.sh"]
