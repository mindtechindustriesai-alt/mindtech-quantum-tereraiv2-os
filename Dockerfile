FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ cmake \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --only-binary :all: -r requirements.txt

# Copy application
COPY mqos/ ./mqos/
COPY dashboard/ ./dashboard/
COPY scripts/ ./scripts/

# Create non-root user
RUN useradd -m -u 1000 mindtech && chown -R mindtech:mindtech /app
USER mindtech

EXPOSE 8000 9090 8501

CMD ["uvicorn", "mqos.api.rest_api:app", "--host", "0.0.0.0", "--port", "8000"]
