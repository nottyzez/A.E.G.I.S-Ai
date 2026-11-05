FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    TF_CPP_MIN_LOG_LEVEL=2

# OpenCV (imported by the ensemble) needs these two shared libraries; the slim
# image ships neither.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Requirements first so a code change does not reinstall TensorFlow (~600 MB).
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# --workers 1 is mandatory: the model needs 1.2-1.5 GB at load, and the command
# queue + current_hardware_status are per-process. Two workers would serve two
# different states and split the dashboard from the ESP32.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=120s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=4).status == 200 else 1)"
