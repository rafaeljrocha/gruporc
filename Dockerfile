FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DATA_DIR=/data \
    APP_HOST=0.0.0.0 \
    APP_PORT=8000 \
    GUNICORN_WORKERS=2 \
    SESSION_LIFETIME_MIN=60 \
    PROXY_FIX=1 \
    COOKIES_SEGUROS=1
WORKDIR /app
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl tini \
 && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/       ./app/
COPY static/    ./static/
COPY templates/ ./templates/
COPY wsgi.py    ./wsgi.py
VOLUME ["/data"]
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/healthz || exit 1
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["sh", "-c", "exec gunicorn --workers ${GUNICORN_WORKERS:-2} \
     --bind 0.0.0.0:8000 \
     --access-logfile - --error-logfile - \
     --forwarded-allow-ips=* \
     --timeout 60 \
     wsgi:app"]
