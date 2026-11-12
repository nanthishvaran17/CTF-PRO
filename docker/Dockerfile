FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    CTFX_MODE=LOCAL

RUN apt-get update && apt-get install -y --no-install-recommends \
    p7zip-full \
    binwalk \
    tshark \
    ffmpeg \
    git \
    libimage-exiftool-perl \
    tesseract-ocr \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY plugins/ ./plugins/
COPY docs/ ./docs/
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

RUN mkdir -p /app/data/uploads /app/data/artifacts /app/data/reports /app/data/cache

EXPOSE 8000

CMD ["uvicorn", "backend.ctfx.main:app", "--host", "0.0.0.0", "--port", "8000"]
