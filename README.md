# 📱 Skin Patient App

> YOLOv8n · EfficientNetB0 기반 AI 피부 분석 서비스 · FastAPI + Docker + Google Cloud Run 배포 · RAG 기반 진단 신뢰성 안전장치 확장

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=flat&logo=tensorflow&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Google Cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=flat&logo=googlecloud&logoColor=white)
![ChromaDB](https://img.shields.io/badge/ChromaDB-FF6600?style=flat&logoColor=white)

**한 줄 요약** : mAP50 99.1% 탐지 모델에 신뢰도 게이트 기반 RAG 안전장치를 더해, 저확신 결과는 차단하고 고확신 결과에는 임상 근거를 붙이는 피부 분석 서비스입니다.

🔗 [배포 바로가기](https://skin-api-965279369783.asia-northeast3.run.app) · 📄 [API 명세](https://skin-api-965279369783.asia-northeast3.run.app/docs)

---

<a id="demo-top"></a>
## 🎯 신뢰도에 따른 응답 분기 (실제 배포 화면)

FFHQ 이미지로 배포 사이트를 직접 테스트해, 신뢰도 게이트가 실제로 응답을 어떻게 차등화하는지 확인했습니다.

| 저확신 케이스 (근거 생략) | 고확신 케이스 (RAG 근거 생성) |
|:---:|:---:|
| <img src="https://github.com/user-attachments/assets/fe2479ce-e8a0-4c1d-a758-7b5710d2cf51" width="280" /> | <img src="https://github.com/user-attachments/assets/7af08b14-83bb-4d2f-b0ab-83b658bccb62" width="280" /> |
| 피부 상태 신뢰도 52% → 게이트 차단, "질환/상태 판정 결과가 불확실하여 근거 기반 설명을 생략합니다" 안내 | 피부 질환 신뢰도 94% → 게이트 통과, ChromaDB 검색 기반 근거(유사도 60%)와 출처 링크 제공 |

같은 UI, 같은 추천 로직 위에서도 신뢰도 수준에 따라 근거 제공 여부가 자동으로 분기됩니다. 설계 배경은 [RAG 기반 진단 신뢰성 안전장치](#rag-safety) 섹션에서 자세히 다룹니다.

---

## 목차

- [프로젝트 개요](#-프로젝트-개요)
- [핵심 성과](#-핵심-성과)
- [배포](#-배포)
- [기술 스택](#-기술-스택)
- [AI 분석 파이프라인](#-ai-분석-파이프라인)
- [모델 성능](#-모델-성능)
- [RAG 기반 진단 신뢰성 안전장치](#rag-safety)

---

## 📌 프로젝트 개요

얼굴 이미지에서 피부 질환·상태를 탐지하고 피부 타입을 분류하는 CV 파이프라인을 설계·학습·배포한 프로젝트입니다.

**왜 이 프로젝트인가**
사진 한 장으로 피부 상태를 확인하고 제품 구매나 진료 예약까지 바로 이어지는 서비스를 만들었습니다. AI 분석 → 화장품 추천 → 의사 비대면 진료 순서로 파이프라인을 구성한 이유는, 남성 피부 관리에 대한 관심이 늘면서 이런 흐름에 대한 수요가 있다고 판단했기 때문입니다.

| 기능 | 설명 |
|:----|:----|
| 🔬 AI 피부 분석 | 사진 업로드 → 피부 타입·질환·상태 즉시 진단 |
| 🏥 의료진 상담 | 진료 요청서 작성 · 온라인 예약 · 진단 내역 조회 |
| 💄 화장품 추천 | 분석 결과 기반 AI 맞춤 제품 추천 |
| 🛡️ 진단 신뢰성 안전장치 | 저확신 결과 차단 + RAG 기반 임상 근거 생성 (개인 확장) |

**프로젝트 타임라인**

| 시점 | 내용 | 형태 |
|:----|:----|:----|
| 2025.03 ~ 2025.06 | AI 파이프라인 설계·학습 (팀 프로젝트) | 4인 팀, AI 파트 기여도 100% |
| 2026.04 | 배포 (Cloud Run) | 개인 확장 |
| 2026.07말 ~ 2026.08 | RAG 기반 진단 신뢰성 안전장치 확장 | 개인 확장 |

---

## ⚡ 핵심 성과

- **데이터 규모** : AI-Hub · Kaggle · Google 자체 수집 포함 총 **29,000장** 피부 이미지 학습
- **CLS_REMAP 라벨 재설계** : 임상 분류 기준을 서비스 목적에 맞게 재구조화, mAP50 **0.34 → 0.99** 달성
- **모델 성능** (validation 기준) : 피부 질환 탐지 mAP50 **99.1%** · 상태 탐지 **97.5%** · 타입 분류 Accuracy **76%**
- **RAG 기반 진단 신뢰성 안전장치** (개인 확장) : 신뢰도 게이트 설계로 설명 가능 비율 **5.7% → 80.0%** 개선
- **학습-서빙 정합성 버그 발견·수정** : 배포 전처리가 학습 시와 달라 타입 모델이 입력과 무관하게 상수 출력 → 원인 규명 후 정상화
- **정량적 신뢰성 검증** : FFHQ unseen 이미지 기준 최종 응답 모순율 **8.6%** 측정, 응답 신뢰성을 수치로 검증
- **AI 파이프라인 전 구간 설계** : 모델 학습부터 서빙, 배포, 신뢰성 검증까지 AI 파트를 처음부터 끝까지 설계·구현
- **팀원 앱 연동 검증** : Android Studio 에뮬레이터로 Cloud Run 백엔드 실연동 확인

---

## 🚀 배포

🔗 **배포 URL** : https://skin-api-965279369783.asia-northeast3.run.app

📄 **API 명세 (Swagger)** : https://skin-api-965279369783.asia-northeast3.run.app/docs

실제 동작 화면(저확신/고확신 케이스)은 [최상단 데모](#demo-top)에서 확인하실 수 있습니다.

### 배포 구조

| 구성 요소 | 역할 |
|:---------|:----|
| Google Cloud Run | 서버리스 컨테이너 실행, 트래픽 없을 때 비용 0으로 소규모 서비스에 적합 |
| Artifact Registry | Docker 이미지 저장 |
| Google Cloud Storage | AI 모델 파일(`.pt`, `.h5`) 분리 저장, Docker 빌드 크기 최소화 |
| Supabase PostgreSQL | 분석 결과 저장 |
| ChromaDB | RAG 검색용 벡터 저장소 (질병관리청·서울아산병원 등 의료기관 자료 근거) |
| UptimeRobot | 5분 주기 헬스체크로 cold start 없는 응답 속도 유지 |

---

## 🧰 기술 스택

| 분류 | 기술 |
|:----|:----|
| AI 모델 | Python · TensorFlow · Keras · YOLOv8n · EfficientNetB0 · OpenCV |
| RAG · LLM | ChromaDB · Groq(LLM) |
| Backend | Python · FastAPI |
| Database | Supabase PostgreSQL |
| Deployment | Docker · Google Cloud Run · Artifact Registry · Google Cloud Storage · UptimeRobot |

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

### 기술 선택 근거

| 모델 | 선택 이유 |
|:----|:----|
| YOLOv8n | EfficientDet, MobileNetV2와 비교 검증한 결과 속도·정확도를 함께 확보할 수 있는 모델로 최종 선택 |
| EfficientNetB0 | 피부 타입은 국소적 특징보다 전체 질감이 중요해 이미지 전체 패턴 학습에 적합, 2-Phase Fine-tuning 적용 |
| FastAPI | Python 네이티브로 AI 모델과 직접 연동, 자동 Swagger 문서 제공 |
| Google Cloud Run | 트래픽 없을 때 비용 0, 컨테이너 기반이라 환경 의존성 문제 최소화 |

### 라벨 구조 재설계 : CLS_REMAP

유사 질환·상태가 임상 분류 기준에 따라 라벨상 과도하게 세분화되어 있어, 데이터 양이 아닌 **라벨 구조 자체**가 성능의 병목이라고 판단했습니다. 유사 클래스를 서비스 목적에 맞게 통합하는 CLS_REMAP을 설계해 mAP50을 0.34에서 0.99로 끌어올렸습니다. 이 과정에서 개발 환경도 목적에 맞게 단계적으로 전환했습니다.

| 단계 | 환경 | 목적 |
|:----|:----|:----|
| 1차 | Google Colab (무료 GPU) | 초기 프로토타입 검증 |
| 2차 | Docker + RTX 3060Ti 로컬 | 컨테이너 기반 재현 가능한 학습 환경 구성 |
| 최종 | Colab A100 | CLS_REMAP + YOLOv8n 조합으로 고성능 학습 완료 |

---

## 🩺 모델 성능

> 아래 수치는 모두 **validation 기준**이며, 실서비스 신뢰도를 높이기 위해 외부 이미지 검증 루프를 파이프라인에 별도로 포함시켰습니다.

| 태스크 | 핵심 지표 | 결과 |
|:------|:---------|:----|
| 피부 질환 탐지 | mAP50 / mAP50-95 | 0.991 / 0.977 |
| 피부 상태 탐지 | mAP50 / mAP50-95 | 0.975 / 0.787 |
| 피부 타입 분류 | Accuracy / Macro F1 | 0.76 / 0.76 |

### 피부 질환 탐지 (YOLOv8n)

**mAP50 0.991 · mAP50-95 0.977**

<img src="https://github.com/user-attachments/assets/43f02cdb-5c08-4487-a724-3e87590daae0" width="80%" />

<img src="https://github.com/user-attachments/assets/eda3b83a-b2c0-4fd8-ac51-3b25b54c6afa" width="65%" />

**학습 전략** : JSON → YOLO 포맷 변환 · 염증성 질환 → `inflammatory` 통합 · Epoch 60 / LR 0.002 → Cosine Annealing

mAP50-95로 박스 정합도를 추가 확인하고, 클래스별·외부 이미지 반응까지 함께 점검해 과적합 가능성을 검증했습니다.

---

### 피부 상태 탐지 (YOLOv8n)

**mAP50 0.975 · mAP50-95 0.787**

<img src="https://github.com/user-attachments/assets/e0b97ed0-05c2-4289-b10f-23c6d7a4cb25" width="80%" />

<img src="https://github.com/user-attachments/assets/7a24a45f-e6e1-48e0-a3d2-df78345fbc3a" width="65%" />

**학습 전략** : `pigmentation` · `pore` → `lesion` 통합 · Albumentations 증강 · Input 1024×1024 / Epoch 10

---

### 피부 타입 분류 (EfficientNetB0)

**Accuracy 0.76 · Macro F1 0.76**

<img src="https://github.com/user-attachments/assets/96eb4ec6-4f92-46f5-b617-aeba82a90fe9" width="60%" />

**학습 전략** : GlobalAveragePooling → Dropout(0.3) → Dense Softmax · MixUp · CutMix / Focal Loss · 2-Phase Fine-tuning

클래스별 데이터 수 차이로 Accuracy만 보면 특정 클래스에 치우친 결과가 나올 수 있어, Macro F1을 함께 확인하는 평가 체계를 적용했습니다.

---

<a id="rag-safety"></a>
## 🛡️ RAG 기반 진단 신뢰성 안전장치 (개인 확장, 2026.08)

### 설계 목적

모델 출력(신뢰도 숫자)을 그대로 노출하는 대신, 신뢰도 수준에 따라 응답을 차등화하는 안전장치를 설계했습니다. 고확신 결과에는 질병관리청·서울아산병원 등 의료기관 공식 자료 기반의 임상 근거를 함께 제공하고, 저확신 결과는 근거 없는 진단 설명이 노출되지 않도록 차단합니다. 실제 동작 화면은 [최상단 데모](#demo-top)를 참고하세요.

### 구조 : 신뢰도 게이트 + RAG

<img src="https://github.com/user-attachments/assets/9347b033-3fb0-4033-b833-5b8506f3a3bb" width="480" />

### 설계 디테일 : 타입 신뢰도를 게이트에서 제외한 이유

1. 질환·상태는 진단적 분류, 타입(건성/지성/복합성)은 성질 분류로 판단 범주 자체가 다릅니다.
2. 질병관리청·서울아산병원 등 의료기관 코퍼스는 진단 목적 자료라, 진단 근거 생성에는 질환·상태 신뢰도가 더 적합합니다.
3. 세 모델의 신뢰도 특성을 개별적으로 분석한 뒤 게이트 기준에 반영해, 특정 항목이 다른 항목의 응답까지 막지 않도록 설계했습니다.

### 버그 발견 : 학습-서빙 정합성 (Training-Serving Skew)

안전장치를 검증하는 과정에서, 피부 타입 모델이 입력 이미지와 무관하게 거의 동일한 결과(신뢰도 35.8% 고정)를 내고 있다는 것을 발견했습니다. 원인은 EfficientNet의 실제 `preprocess_input`이 identity 함수(정규화가 모델 내부에 포함되어 있어 0\~255 원본을 그대로 받아야 함)인데, 서빙 코드가 이를 `x/255.0`으로 잘못 구현하고 전처리 단계에서 이미 한 번 나눈 값을 그대로 전달해 이중 정규화가 발생한 것이었습니다. 원인을 규명해 수정한 뒤, 이미지별로 반응하는 정상적인 예측(신뢰도 37\~75% 분포)으로 회복했습니다.

### 정량적 검증

FFHQ unseen 이미지 35장으로 안전장치의 실제 동작을 검증했습니다. 모델 성능 지표뿐 아니라 응답 신뢰성 자체도 수치로 확인했습니다.

- **설명 가능 비율 5.7% → 80.0%** : 게이트 설계 변경(타입 신뢰도 제외)만으로 확보한 개선폭
- **최종 응답 모순율 8.6%** : 근거 생성 결과의 논리적 일관성을 별도 지표로 관리

---

## 🛠 시스템 구조

<img width="1112" alt="시스템 구조" src="https://github.com/user-attachments/assets/61a8565f-f926-4a1f-82b3-507316557c99" />

<img width="1122" alt="배포 구조" src="https://github.com/user-attachments/assets/58ab7807-6e7b-4a1a-a651-61db0996fc63" />

---

## 🔍 앱 화면

<img width="1075" alt="앱 화면1" src="https://github.com/user-attachments/assets/ed79a8b2-a3b6-4d6e-95d1-a51fd3951a52" />

<img width="1080" alt="앱 화면2" src="https://github.com/user-attachments/assets/c78bf23d-74f5-4052-982a-be0151bb6cf8" />

---

## 👥 팀원 및 역할

| 이름 (포지션) | 담당 업무 |
|:-------------|:---------|
| 이동우 (AI / 배포) | AI 파이프라인 설계·학습 (질환·상태 탐지 / 타입 분류)<br>FastAPI 서버 구현 및 Cloud Run 배포 전담<br>(개인 확장) RAG 기반 진단 신뢰성 안전장치 설계 |
| 이승현 (Front-end) | |
| 이충민 (Full-Stack) | |
| 진완규 (Back-end) | 화장품 추천 알고리즘 및 서버 구축 |

---

## 🗄️ 데이터베이스 구조

백엔드 담당(진완규)이 설계한 스키마입니다. 전체 시스템 이해를 위한 참고용으로 남겨둡니다.

| 테이블 | 역할 |
|:------|:----|
| skin_analysis_results | AI 분석 결과 메인 |
| skin_analysis_concerns | 피부 고민사항 |
| skin_analysis_recommendations | AI 추천사항 |
| skin_analysis_images | 분석 이미지 메타데이터 |

자세한 스키마는 [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) 참조
