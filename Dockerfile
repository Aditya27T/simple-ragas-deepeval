# ============================================================
# Dockerfile untuk Simple RAGAS & DeepEval Evaluator
# ============================================================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements terlebih dahulu (untuk memanfaatkan layer cache Docker)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy semua script Python
COPY task1_fetch_scenario.py .
COPY task2_run_openrouter.py .
COPY task3_evaluate.py .

# Direktori untuk data yang di-mount dari host (dataset & output JSON)
VOLUME ["/app/data"]

# Default env vars (akan di-override oleh .env atau docker-compose)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEEPEVAL_TELEMETRY_OPT_OUT=YES

# Default command: tampilkan bantuan
CMD ["python", "--version"]
