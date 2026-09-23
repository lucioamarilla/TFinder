# TFinder API · imagen base AE2 (B01)
# Misma version de Python que el host de desarrollo (3.12).
# Entrada real de la app: app.main:app (el main.py de la raiz es residuo AE1).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias primero (aprovecha capa cache del build)
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Codigo de la app
COPY app ./app

EXPOSE 8001

# --host 0.0.0.0 es obligatorio dentro del contenedor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]