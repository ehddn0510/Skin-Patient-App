# 📱 Skin Patient App

> YOLOv8n + EfficientNetB0 기반 AI 피부 분석 서비스 — FastAPI + Docker + Google Cloud Run 배포 

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=flat&logo=tensorflow&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=flat&logo=googlecloud&logoColor=white)

---

## ⚡ 핵심 성과

- **데이터 규모** — AI-Hub · Kaggle · Google 자체 수집 포함 총 **29,000장** 피부 이미지 학습
- **CLS_REMAP 라벨 재설계** — 유사 클래스 통합 재학습으로 mAP50 **0.34 → 0.99** 달성
- **모델 성능** (validation 기준) — 피부 질환 탐지 mAP50 **99.1%** · 상태 탐지 **97.5%** · 타입 분류 Accuracy **76%**
- **배포 트러블슈팅 3건** — OOM · cold start · numpy 버전 충돌 직접 해결
- **팀원 앱 연동 검증** — Android Studio 에뮬레이터로 Cloud Run 백엔드 실연동 확인

---

## 🚀 배포

🔗 **배포 URL**: https://skin-api-965279369783.asia-northeast3.run.app

📄 **API 명세 (Swagger)**: https://skin-api-965279369783.asia-northeast3.run.app/docs

### 📱 서비스 동작 화면

> 이미지를 업로드하면 피부 타입 · 질환 · 상태를 confidence score와 함께 출력합니다.

<img width="725" height="940" alt="서비스 동작 화면" src="https://github.com/user-attachments/assets/09a338d1-c64a-49de-b007-589c93d804d9" />

### 배포 구조

| 구성 요소 | 역할 |
|:---------|:----|
| Google Cloud Run | 서버리스 컨테이너 실행 |
| Artifact Registry | Docker 이미지 저장 |
| Google Cloud Storage | AI 모델 파일(`.pt`, `.h5`) 분리 저장 |
| Supabase PostgreSQL | 분석 결과 저장 |
| UptimeRobot | 5분 주기 헬스체크 (cold start 방지) |

### 트러블슈팅

| 문제 | 원인 | 해결 |
|:----|:----|:----|
| TensorFlow 런타임 크래시 | ultralytics가 numpy 2.x로 업그레이드 | `numpy==1.26.4` Dockerfile 버전 고정 |
| Cloud Build UnicodeDecodeError | 바이너리 모델 파일이 소스에 포함됨 | `.gcloudignore`로 제외 + GCS 분리 저장 |
| Cold start 15~20초 지연 | 서버리스 컨테이너 비활성화 | UptimeRobot 헬스체크로 즉시 접속 수준으로 개선 |

---

## 🎯 기술 스택

| 분류 | 기술 |
|:----|:----|
| AI | Python · TensorFlow · YOLOv8n · EfficientNetB0 · OpenCV |
| Backend | Python · FastAPI |
| Database | Supabase PostgreSQL · Pinecone |
| Deployment | Docker · Google Cloud Run · Artifact Registry · GCS · UptimeRobot |
| Frontend | Android (이승현 담당) |

---

## 👥 팀원 및 역할

| 이름 (포지션) | 담당 업무 |
|:-------------|:---------|
| 이동우 (AI / 배포) | AI 파이프라인 설계·학습 (질환·상태 탐지 / 타입 분류)<br>FastAPI 서버 구현 및 Cloud Run 배포 전담 |
| 이승현 (Front-end) |  |
| 이충민 (Full-Stack) | |
| 진완규 (Back-end) | 화장품 추천 알고리즘 및 서버 구축 |

---

## 📌 프로젝트 개요

얼굴 이미지에서 피부 질환·상태를 탐지하고 피부 타입을 분류하는 CV 파이프라인을 설계·학습·배포한 프로젝트입니다.

- 남성 피부 미용 관심 증가에 따른 맞춤형 피부 분석 수요 대응
- AI 피부 분석 → 화장품 추천 → 의사 비대면 진료 연계

| 기능 | 설명 |
|:----|:----|
| 🔬 AI 피부 분석 | 사진 업로드 → 피부 타입·질환·상태 즉시 진단 |
| 🏥 의료진 상담 | 진료 요청서 작성 · 온라인 예약 · 진단 내역 조회 |
| 💄 화장품 추천 | 분석 결과 기반 AI 맞춤 제품 추천 |

---

## 🛠 시스템 구조

<img width="1112" alt="시스템 구조" src="https://github.com/user-attachments/assets/61a8565f-f926-4a1f-82b3-507316557c99" />

<img width="1122" alt="배포 구조" src="https://github.com/user-attachments/assets/58ab7807-6e7b-4a1a-a651-61db0996fc63" />

---

## 🔍 앱 화면

<img width="1075" alt="앱 화면1" src="https://github.com/user-attachments/assets/ed79a8b2-a3b6-4d6e-95d1-a51fd3951a52" />

<img width="1080" alt="앱 화면2" src="https://github.com/user-attachments/assets/c78bf23d-74f5-4052-982a-be0151bb6cf8" />

---

## 🧠 AI 분석 파이프라인

객체 탐지(Detection)와 분류(Classification)를 분리한 **2단계 파이프라인**으로 구성했습니다.

```
입력 이미지
    ↓
얼굴 영역 탐지 (YOLOv8n) → 얼굴 크롭
    ↓
피부 질환 탐지 (YOLOv8n)       ┐
피부 상태 탐지 (YOLOv8n)       ├── 바운딩 박스 + confidence score
피부 타입 분류 (EfficientNetB0) ┘
    ↓
분석 결과 DB 저장 → 화장품 추천 · 진료 시스템 연동
```

**개발 환경 변천**

| 단계 | 환경 | 비고 |
|:----|:----|:----|
| 1차 시도 | Google Colab (무료 GPU) | 초기 프로토타입 · CUDA 충돌 |
| 2차 시도 | Docker + RTX 3060Ti 로컬 | 컨테이너 환경 구성 |
| 최종 | Colab A100 | YOLOv8n + 고성능 GPU 학습 완료 |

**기술 선택 근거**

| 모델 | 선택 이유 |
|:----|:----|
| YOLOv8n | EfficientDet은 라벨 구조 문제로 불안정, MobileNetV2는 정확도 미달 → 속도·정확도 동시 확보 |
| EfficientNetB0 | 피부 타입은 전체 질감이 중요 → 이미지 전체 패턴 학습에 적합, 2-Phase Fine-tuning 적용 |

---

## 🩺 모델 성능

> 아래 수치는 모두 **validation 기준**입니다.

### 피부 질환 탐지 (YOLOv8n)

**mAP50 0.991 · mAP50-95 0.977**

<img src="https://github.com/user-attachments/assets/43f02cdb-5c08-4487-a724-3e87590daae0" width="80%" />

<img src="https://github.com/user-attachments/assets/eda3b83a-b2c0-4fd8-ac51-3b25b54c6afa" width="65%" />

**학습 전략** — JSON → YOLO 포맷 변환 · 염증성 질환 → `inflammatory` 통합 · Epoch 60 / LR 0.002 → Cosine Annealing

---

### 피부 상태 탐지 (YOLOv8n)

**mAP50 0.975 · mAP50-95 0.787**

<img src="https://github.com/user-attachments/assets/e0b97ed0-05c2-4289-b10f-23c6d7a4cb25" width="80%" />

<img src="https://github.com/user-attachments/assets/7a24a45f-e6e1-48e0-a3d2-df78345fbc3a" width="65%" />

**학습 전략** — `pigmentation` · `pore` → `lesion` 통합 · Albumentations 증강 · Input 1024×1024 / Epoch 10

---

### 피부 타입 분류 (EfficientNetB0)

**Accuracy 0.76 · Macro F1 0.76**

<img src="https://github.com/user-attachments/assets/96eb4ec6-4f92-46f5-b617-aeba82a90fe9" width="60%" />

**학습 전략** — GlobalAveragePooling → Dropout(0.3) → Dense Softmax · MixUp · CutMix / Focal Loss · 2-Phase Fine-tuning

---

## 🗄️ 데이터베이스 구조

| 테이블 | 역할 |
|:------|:----|
| skin_analysis_results | AI 분석 결과 메인 |
| skin_analysis_concerns | 피부 고민사항 |
| skin_analysis_recommendations | AI 추천사항 |
| skin_analysis_images | 분석 이미지 메타데이터 |

자세한 스키마는 [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) 참조
