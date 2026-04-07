FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY app/ app/
COPY media/ media/
COPY alembic/ alembic/
COPY alembic.ini alembic.ini
# COPY .env .env # You should pass env vars via docker-compose instead
# We still copy frontend assets since FastAPI might serve them statically.

# Default command for the API
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
