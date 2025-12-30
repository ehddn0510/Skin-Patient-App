# 📱 Skin Patient App

환자용 피부 건강 관리 앱 - 피부 상태를 기록하고 의료진의 진단을 받을 수 있는 환자용 앱입니다.

## 📌 프로젝트 개요
### 기획 의도
- 최근 남성들의 화장품 및 피부 미용에 대한 관심이 증가함에 따라 맞춤형 화장품 및 관리 제품 팔요성 증대 
- 정확한 피부 분석 및 의사와의 상담 필요

### 차별화 포인트
- 의사의 비대면 진료를 통한 진료 및 약 처방 가능
- AI를 활용한 피부 분석을 통해 맞춤형 화장품 추천


## ✨ 주요 기능

### 🔬 AI 피부 분석
- **실시간 AI 피부 분석**: 사진 촬영으로 즉시 피부 상태 진단
- **분석 내역 저장**: 모든 AI 분석 결과를 자동으로 데이터베이스에 저장
- **분석 내역 조회**: 과거 분석 결과 조회 및 변화 추이 확인
- **상세 분석 정보**: 피부 타입, 고민사항, 추천사항, 신뢰도 점수 등 제공

### 🏥 의료진 상담
- **진료 요청서 작성**: 증상, 기간, 심각도 등 상세 정보 입력
- **온라인 예약**: 병원 및 의사 선택하여 예약
- **진단 내역 조회**: 과거 진료 기록 및 처방전 확인

### 💄 화장품 추천
- **AI 맞춤 추천**: 피부 분석 결과 기반 제품 추천
- **추천 내역 관리**: 과거 추천 결과 저장 및 조회
- **제품 상세 정보**: 가격, 리뷰, 성분 등 상세 정보 제공

---


## 🎯 기술 스택
- **Frontend**: 
- **Backend**: Python, Fast API, 
- **Database**: PostgreSQL, pinecone
- **보안 및 암호화**: 
- **Deployment**: 
- **AI**: kosebert, 

---
## 🗄️ 데이터베이스 구조

### AI 피부 분석 관련 테이블
- **skin_analysis_results**: AI 분석 결과 메인 테이블
- **skin_analysis_concerns**: 피부 고민사항 저장
- **skin_analysis_recommendations**: AI 추천사항 저장
- **skin_analysis_images**: 분석 이미지 메타데이터

자세한 데이터베이스 스키마는 [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)를 참조하세요.

---

## 🧑‍💻 팀원 및 역할

| 이름 (포지션) | 담당 업무 |
|:-------------|:-----|
| 이동우 (AI) |  |
| 이승현 (Front-end) |  |
| 이충민 (Full-Stack) |  |
| 진완규 (Back-end) | 화장품 추천 알고리즘 및 서버 구축 |

---
## 🛠 시스템 구조
<img width="1112" height="626" alt="Image" src="https://github.com/user-attachments/assets/61a8565f-f926-4a1f-82b3-507316557c99" />

<img width="1122" height="622" alt="Image" src="https://github.com/user-attachments/assets/58ab7807-6e7b-4a1a-a651-61db0996fc63" />

---
## 🔍 주요 기능 화면

<img width="1075" height="485" alt="Image" src="https://github.com/user-attachments/assets/ed79a8b2-a3b6-4d6e-95d1-a51fd3951a52" />

<img width="1080" height="480" alt="Image" src="https://github.com/user-attachments/assets/c78bf23d-74f5-4052-982a-be0151bb6cf8" />

<img width="1070" height="479" alt="Image" src="https://github.com/user-attachments/assets/e8e4650c-4e33-4dfc-adeb-f6f9631b4090" />

<img width="1073" height="481" alt="Image" src="https://github.com/user-attachments/assets/acd9b9cd-7378-4cd9-a6dd-64e4de58d762" />

<img width="1069" height="481" alt="Image" src="https://github.com/user-attachments/assets/7e363194-d420-4d3f-b88c-50195a1efe0e" />

<img width="1082" height="485" alt="Image" src="https://github.com/user-attachments/assets/0f9d4a4f-84f0-4f13-93f2-eeb8a9af4b53" />

<img width="1062" height="476" alt="Image" src="https://github.com/user-attachments/assets/33663bc9-eb63-413c-bc87-d98dbb0124d7" />

<img width="1075" height="475" alt="Image" src="https://github.com/user-attachments/assets/92a7d649-e81f-497b-848c-65ec7ec715b1" />


🤖 AI 피부 분석 모델

본 프로젝트의 AI 파트는 모바일 환경에서도 실시간 사용이 가능한 경량 모델을 목표로
객체 탐지(Object Detection) + 분류(Classification)를 분리한 2단계 구조로 설계

🧠 AI 전체 흐름
사용자 얼굴 이미지
        ↓
YOLOv8n (얼굴 탐지)
        ↓
얼굴 영역 크롭
        ↓
YOLOv8n (피부 질환 / 상태 탐지)
        ↓
EfficientNetB0 (피부 타입 분류)
        ↓
분석 결과 저장 및 추천 시스템 연동

🔍 피부 질환 · 상태 탐지 (YOLOv8n)
✔️ 개요

얼굴 내부의 피부 질환 및 상태 위치를 바운딩 박스로 탐지

모바일 실시간 적용을 고려해 YOLOv8 시리즈 중 가장 경량인 YOLOv8n 사용

✔️ 활용 방식

얼굴 탐지

yolov8n-face-lindevs.pt 모델로 얼굴 영역 자동 검출

피부 상태 탐지

크롭된 얼굴 이미지에 대해 YOLOv8n 파인튜닝 모델 적용

여드름, 주름, 건조, 처짐 등 클래스별 탐지

<img src="https://github.com/user-attachments/assets/ed79a8b2-a3b6-4d6e-95d1-a51fd3951a52" width="800"/>
🧪 데이터 전처리

JSON 어노테이션 → YOLO 포맷 변환

다양한 이미지 크기에 대응하기 위한 좌표 정규화

시각적으로 유사한 클래스 통합

pigmentation, pore → lesion

지루·주사 등 염증성 질환 → inflammatory

Albumentations 기반 데이터 증강 적용
(회전, 반전, 밝기·대비 조정, 블러 등)

클래스 불균형 완화를 위한 Stratified split

⚙️ 학습 설정 (PPT 기준)

Input Size: 1024 × 1024

Epoch: 10

Warm-up: 3 epoch

Learning Rate: 0.002 → Cosine Annealing

Momentum: 0.937

실시간 적용을 고려한 YOLOv8n fine-tuning

📊 탐지 결과 예시
<img src="https://github.com/user-attachments/assets/e8e4650c-4e33-4dfc-adeb-f6f9631b4090" width="800"/>

얼굴 내 피부 상태 4종류 탐지

클래스 이름과 confidence score 시각화

염증성 질환은 inflammatory로 통합 예측

🧴 피부 타입 분류 (EfficientNetB0)
✔️ 개요

얼굴 전체 이미지를 기반으로 피부 타입 분류

클래스: dry / normal / oily

YOLO로 얼굴을 자동 크롭한 후 분류 모델에 입력

<img src="https://github.com/user-attachments/assets/acd9b9cd-7378-4cd9-a6dd-64e4de58d762" width="800"/>
🧪 데이터 전처리

YOLOv8n(face 모델)로 얼굴 영역 자동 추출

Albumentations 및 OpenCV 기반 증강 적용 → 데이터 수 확장

Resize: 224 × 224

Train / Valid / Test = 8 : 1 : 1

⚙️ 학습 구조 및 전략

Backbone: EfficientNetB0

분류기 구조

GlobalAveragePooling
→ Dropout(0.3)
→ Dense (Softmax)


MixUp · CutMix 적용

Focal Loss 적용

Cosine Annealing 스케줄

2단계 학습

Phase 1: Backbone 고정

Phase 2: 하위 레이어 Fine-tuning

📈 성능 평가 기준

Accuracy

Recall

F1-score

외부 이미지 및 다양한 환경에서도 작동 가능한 일반화 성능 중점 평가

🧑‍💻 AI 담당 역할 (이동우)

YOLOv8n 기반 피부 질환/상태 탐지 모델 파인튜닝

EfficientNetB0 기반 피부 타입 분류 모델 학습

JSON → YOLO 변환 및 데이터 전처리 파이프라인 구축

클래스 통합 전략 수립을 통한 학습 안정성 개선

모바일 실시간 적용을 고려한 모델 구조 설계

모델 추론 결과를 서버(FastAPI)와 연동 가능한 형태로 설계

🔧 향후 개선 방향

mAP 기반 탐지 성능 정량 평가 고도화

피부 상태 세부 클래스 확장

조명·연령·촬영 환경에 대한 일반화 강화
