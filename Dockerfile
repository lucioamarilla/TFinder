# TFinder AE2 · imagen base por servicio (B02)
# Un único Dockerfile sirve a los 4 servicios; el paquete se elige con ARG SERVICE:
#   docker compose build mesas-api   -> mesas_api   (8001)
#   docker compose build builds-api  -> builds_api  (8002)
#   docker compose build feed-api    -> feed_api    (8003)
#   docker compose build notif-api   -> notif_api   (8004)
ARG SERVICE=mesas_api

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias primero (aprovecha capa cache del build)
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Codigo del servicio elegido + plantilla compartida (app/infra)
ARG SERVICE
COPY ${SERVICE} ./${SERVICE}
COPY app ./app

ENV PORT=8001
ENV SERVICE=${SERVICE}

EXPOSE 8001

# --host 0.0.0.0 es obligatorio dentro del contenedor
CMD ["sh", "-c", "uvicorn ${SERVICE}.main:app --host 0.0.0.0 --port ${PORT}"]