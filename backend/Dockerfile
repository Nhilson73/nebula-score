FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/pyproject.toml
COPY backend /app/backend
COPY methodologies /app/methodologies

RUN pip install --no-cache-dir -e "."

ENV PYTHONPATH=/app

CMD ["uvicorn", "backend.app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
