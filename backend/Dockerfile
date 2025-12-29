# Backend Dockerfile for Cloud Run
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy models directory (from parent directory context)
COPY models/ /app/models/

# Cloud Run will set PORT env var automatically
EXPOSE 8080

# Run the application - use PORT env var from Cloud Run
CMD python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}

