FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "hypercorn main:app --bind ${APP_HOST:-0.0.0.0}:${APP_PORT:-8000}"]
