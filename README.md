# 📱 Skin Patient App

환자용 피부 건강 관리 앱 - 피부 상태를 기록하고 의료진의 진단을 받을 수 있는 환자용 앱입니다.

## 📌 프로젝트 개요
### 기획 의도
- 최근 남성들의 화장품 및 피부 미용에 대한 관심이 증가함에 따라 맞춤형 화장품 및 관리 제품 필요성 증대 
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
- **Deployment**: 
- **AI**: Python, TensorFlow, YOLOv8, EfficientNet, OpenCV

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
|:-------------|:---------|
| 이동우 (AI) | YOLOv8n 기반 피부 질환/상태 탐지 모델 파인튜닝<br>EfficientNetB0 기반 피부 타입 분류 모델 파인튜닝<br>AI 데이터 전처리 및 학습 파이프라인 설계 |
| 이승현 (Front-end) |  |
| 이충민 (Full-Stack) | |
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

## 🧠 AI 분석 파이프라인

모바일 환경에서 실시간 처리가 가능하도록  
객체 탐지(Object Detection)와 분류(Classification)를 분리한 **2단계 파이프라인**으로 구성했습니다.

1. **입력 이미지 수집**
   - 사용자가 촬영한 얼굴 이미지 입력

2. **얼굴 영역 탐지 (YOLOv8n)**
   - 얼굴 영역 자동 검출
   - 불필요한 배경 제거

3. **얼굴 영역 크롭**
   - 탐지된 얼굴 영역 기준으로 이미지 크롭
   - 이후 분석 모델 입력 데이터로 사용

4. **피부 질환 / 피부 상태 탐지 (YOLOv8n)**
   - 여드름, 염증성 질환 등 피부 질환 탐지
   - 주름, 건조, 처짐 등 피부 상태 탐지
   - 바운딩 박스 + confidence score 출력

5. **피부 타입 분류 (EfficientNetB0)**
   - 크롭된 얼굴 이미지 기반 분류
   - dry / normal / oily 타입 예측

6. **분석 결과 저장 및 서비스 연동**
   - 분석 결과 DB 저장
   - 화장품 추천 및 진료 시스템과 연동




## 🩺 피부 질환 탐지 모델 (YOLOv8n)

얼굴 내부의 **피부 질환 위치를 바운딩 박스로 탐지**하는 모델로,  
모바일 실시간 적용을 고려해 **YOLOv8 시리즈 중 가장 경량인 YOLOv8n**을 사용

---

### ① 피부 질환 탐지 모델 – 학습 과정

> **Training Loss 및 Precision / Recall / mAP 변화**

<img src="https://github.com/user-attachments/assets/acbe4778-28e9-49d0-83e9-7f1d88822dee" width="85%" />

---

### ② 피부 질환 탐지 모델 – Validation 성능 지표

> **Validation 데이터 기준 Precision, Recall, mAP50, mAP50-95**

<img src="https://github.com/user-attachments/assets/43f02cdb-5c08-4487-a724-3e87590daae0" width="85%" />

---

### ③ 피부 질환 탐지 결과 (Validation 데이터)

> **여드름, 정상, 염증성 질환(inflammatory) 탐지 결과 예시**

<img src="https://github.com/user-attachments/assets/eda3b83a-b2c0-4fd8-ac51-3b25b54c6afa" width="70%" />

---

### ④ 피부 질환 탐지 결과 (추가 Validation 예시)



<img src="https://github.com/user-attachments/assets/4d107171-4927-4bf2-a373-384d13279588" width="70%" />

---

### 사용한 전처리 및 학습 전략
- JSON 어노테이션 → YOLO 포맷 변환
- 다양한 이미지 크기에 대응하기 위한 좌표 정규화
- 염증성 질환(지루·주사 등) → `inflammatory` 클래스로 통합
- Epoch 60 / Early Stopping 10
- Learning Rate 0.002 → Cosine Annealing
- Warm-up 3 epoch

---

## ✨ 피부 상태 탐지 모델 (YOLOv8n)

피부 질환과는 별도로, 얼굴 내 **피부 상태(lesion, wrinkle, dryness, chin sagging)**를  
바운딩 박스로 탐지하는 모델입니다.

---

### ⑤ 피부 상태 탐지 모델 – 학습 과정

> **Training Loss 및 Precision / Recall / mAP 변화**

<img src="https://github.com/user-attachments/assets/ebab128c-8f02-4fb9-9a8e-f1dc3ff06cc4" width="85%" />

---

### ⑥ 피부 상태 탐지 모델 – Validation 성능 지표

> **Validation 데이터 기준 탐지 성능 지표**

<img src="https://github.com/user-attachments/assets/e0b97ed0-05c2-4289-b10f-23c6d7a4cb25" width="85%" />

---

### ⑦ 피부 상태 탐지 결과 (Validation 데이터)

> **lesion / wrinkle / lip_dryness / chin_sagging 탐지 결과**

<img src="https://github.com/user-attachments/assets/7a24a45f-e6e1-48e0-a3d2-df78345fbc3a" width="70%" />

---

### ⑧ 피부 상태 탐지 결과 (추가 Validation 예시)



<img src="https://github.com/user-attachments/assets/799355ae-c2d1-425b-aa5c-9d3b34bb6e7e" width="70%" />

---

### 사용한 전처리 및 학습 전략
- `pigmentation`, `pore` → `lesion` 통합
- Albumentations 기반 데이터 증강
- Stratified split으로 클래스 불균형 완화
- Input 1024×1024 / Batch 64
- Epoch 10 / Warm-up 3
- LR 0.002 → Cosine Annealing / Momentum 0.937

---

## 🧴 피부 타입 분류 모델 (EfficientNetB0)

얼굴 전체 이미지를 기반으로 **피부 타입을 분류**하는 모델입니다.  
YOLO를 통해 얼굴을 자동 크롭한 후 분류 모델에 입력합니다.

---

### ⑨ 피부 타입 분류 결과 (Confusion Matrix)

> **dry / normal / oily 피부 타입 분류 성능**

<img src="https://github.com/user-attachments/assets/96eb4ec6-4f92-46f5-b617-aeba82a90fe9" width="65%" />

---

### 분류 모델 학습 전략
- EfficientNetB0 기반 분류 모델
- GlobalAveragePooling → Dropout(0.3) → Dense Softmax
- MixUp · CutMix / Focal Loss 적용
- Phase 1: Backbone 고정
- Phase 2: 하위 레이어 Fine-tuning

---

