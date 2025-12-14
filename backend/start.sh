#!/bin/sh
set -e

MODEL_PATH="skelo/SKELOv1.pt"
EXAMPLE_PATH="example.jpg"

MODEL_URL="https://drive.google.com/uc?id=18T0X30kh4I2EVv0G93hwnP3h4O2i5tqb"
EXAMPLE_URL="https://drive.google.com/uc?id=1J14cpmGsXOk9QjlC6kARyNqDHXQr5FAV"

mkdir -p skelo

if [ ! -f "$MODEL_PATH" ]; then
  echo "[INFO] Downloading model..."
  gdown --fuzzy -O "$MODEL_PATH" "$MODEL_URL"
fi

if [ ! -f "$EXAMPLE_PATH" ]; then
  echo "[INFO] Downloading example image..."
  gdown --fuzzy -O "$EXAMPLE_PATH" "$EXAMPLE_URL"
fi

exec gunicorn app:app \
  --bind 0.0.0.0:${PORT:-5000} \
  --workers 1 \
  --threads 4 \
  --timeout 180
