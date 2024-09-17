FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    groupadd -g 1000 appuser && \
    useradd -m -u 1000 -g appuser appuser && \
    chown -R appuser:appuser /app

ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PATH="$POETRY_HOME/bin:$PATH"

COPY --chown=appuser:appuser . .

USER appuser

RUN poetry install

ARG BACKEND_PORT
ARG FRONTEND_PORT
ARG JWT_SECRET_KEY
ENV BACKEND_PORT=${BACKEND_PORT} \
    JWT_SECRET_KEY=${JWT_SECRET_KEY} \
    FRONTEND_PORT=${FRONTEND_PORT}

EXPOSE ${BACKEND_PORT}

CMD ["sh", "-c", "poetry run uvicorn api.main:app --host 0.0.0.0 --port ${BACKEND_PORT}"]
