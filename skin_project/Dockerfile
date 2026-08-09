FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgomp1 \
    libgl1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements_prod.txt .
RUN pip install --no-cache-dir -r requirements_prod.txt

COPY . .

# GCS에서 AI 모델 다운로드
RUN mkdir -p "AI tool" && \
    curl -o "AI tool/SkinDisease.pt" "https://storage.googleapis.com/skin-patient-app-models/SkinDisease.pt" && \
    curl -o "AI tool/SkinState.pt" "https://storage.googleapis.com/skin-patient-app-models/SkinState.pt" && \
    curl -o "AI tool/skintype.h5" "https://storage.googleapis.com/skin-patient-app-models/skintype.h5"

ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
