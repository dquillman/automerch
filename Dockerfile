FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Expose port (Cloud Run will set PORT env var)
EXPOSE $PORT

# Use automerch.api.app for the new structure
# Cloud Run will automatically set PORT environment variable
# Use PORT environment variable if set, otherwise default to 8000
CMD exec uvicorn automerch.api.app:app --host 0.0.0.0 --port ${PORT:-8000}
