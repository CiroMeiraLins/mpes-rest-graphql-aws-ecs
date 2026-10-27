FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências do sistema (mínimas). psycopg[binary] evita libpq.
RUN apt-get update && apt-get install -y --no-install-recommends     ca-certificates  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

# Gunicorn em produção
CMD ["gunicorn", "-b", "0.0.0.0:8001", "app:app", "--workers", "2", "--threads", "4", "--timeout", "60"]
