# STAGE 1: Builder Stage (Python 3.13 Alpine)
FROM python:3.13-alpine AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt ./
RUN pip install --no-cache-dir --default-timeout=100 --retries=5 -r requirements.txt && \
    pip install --no-cache-dir --upgrade msgpack>=1.2.1 setuptools>=83.0.0 && \
    pip uninstall -y pip setuptools 2>/dev/null; \
    rm -rf /opt/venv/lib/python*/site-packages/pip* \
           /opt/venv/lib/python*/site-packages/setuptools* \
           /opt/venv/lib/python*/site-packages/pkg_resources \
           /opt/venv/lib/python*/site-packages/_distutils_hack; true

# STAGE 2: Production Runner Stage (Python 3.13 Alpine ~ 0 CVEs)
FROM python:3.13-alpine AS runner

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH"

RUN addgroup -S appgroup && adduser -S appuser -G appgroup && \
    pip uninstall -y setuptools pip 2>/dev/null; \
    rm -rf /usr/local/lib/python*/site-packages/setuptools* \
           /usr/local/lib/python*/site-packages/pkg_resources \
           /usr/local/lib/python*/site-packages/pip* \
           /usr/local/lib/python*/site-packages/msgpack* \
           /usr/local/lib/python*/site-packages/_distutils_hack \
           /usr/local/lib/python*/ensurepip \
           /usr/local/bin/pip*; true

COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appgroup app ./app

USER appuser

EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
