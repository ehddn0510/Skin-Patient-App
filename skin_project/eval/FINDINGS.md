# 진단 신뢰성 Eval — 발견 기록

FFHQ unseen 이미지 35장으로 기존 파인튜닝 모델(재학습 없음, 가중치 그대로)의
진단 신뢰성 파이프라인을 정량 평가한 기록. (`eval/run_contradiction_eval.py`)

---

## 0. 테스트 데이터 출처 및 라이선스 (FFHQ)

- **데이터셋**: Flickr-Faces-HQ (FFHQ), 원래 GAN 벤치마크용으로 제작된 고품질 인물 얼굴 이미지 데이터셋
- **제작**: Tero Karras, Samuli Laine, Timo Aila (NVIDIA)
- **논문**: "A Style-Based Generator Architecture for Generative Adversarial Networks" — https://arxiv.org/abs/1812.04948
- **사용한 하위 세트**: `images1024x1024` (1024×1024 PNG, 전체 70,000장 중 35장 사용)
- **라이선스**:
  - 데이터셋 자체(메타데이터·다운로드 스크립트·문서): NVIDIA가 **CC BY-NC-SA 4.0**으로 제공 — 비상업적 사용/재배포/수정 가능, 단 (a) 논문 인용 출처 표시 (b) 변경 사항 명시 (c) 파생물은 동일 라이선스로 배포해야 함
  - 개별 이미지: Flickr 원저작자가 CC BY 2.0 / CC BY-NC 2.0 / Public Domain Mark 1.0 / CC0 1.0 / 미국 정부 저작물 라이선스 중 하나로 게시 — 모두 비상업적 자유 이용 허용, 일부는 출처 표시·변경사항 명시 요구
  - **명시적 사용 제한**: 안면 인식 기술의 개발·개선 목적으로는 제공되지 않으며 그런 목적으로 사용 금지
- **본 프로젝트에서의 사용 범위**: 비상업적 eval(모순율·안전 게이트 효과 측정)에만 사용, 이미지 자체를 재배포하지 않음, 안면 인식 관련 용도 아님
- **주의**: 추후 README나 외부 공개 자료에 이 eval 결과를 인용할 경우, 위 논문 인용 및 출처 표시를 반드시 포함할 것

---

## 1. 피부 타입 모델 이중 정규화 버그

### 증상

FFHQ 35장을 넣었는데 **35장 전부 동일한 라벨("지성")과 동일한 신뢰도(35.8%, 소수점까지 완전 일치)**가 나옴.
"신뢰도가 낮다"가 아니라 **입력 이미지와 무관하게 항상 같은 값**이 나오는 것을 발견.

### 원인

- 피부 타입 모델(EfficientNetB0)은 원래 **정규화를 모델 내부에 포함**하도록 설계되어 있어서,
  `tensorflow.keras.applications.efficientnet.preprocess_input`은 실제로는 **아무것도 하지 않는 identity 함수**임
  (Keras 공식 소스에 "정규화 로직은 모델 구현에 이미 포함되어 있어, 이 함수는 하위호환을 위한 placeholder"라고 명시됨)
- 그런데 `ai_model_service.py`에서 `.h5` 로드 호환성을 위해 등록한 커스텀 `preprocess_input`이
  `return x / 255.0`으로 잘못 구현되어 있었음
- 여기에 `preprocess_image()`가 이미 입력을 0~1로 정규화(`/255.0`)한 뒤 그대로 타입 모델에 전달하고 있었음
- 결과: **255로 두 번 나눠짐** → 모든 픽셀 값이 0에 수렴 → 모델 입장에서 모든 이미지가 "거의 새까만 이미지"로 보임
  → 이미지 내용과 무관하게 거의 동일한 출력

### 진단 방법

1. `preprocess_image()` 출력 배열이 이미지마다 실제로 다른지 확인 (mean/std 비교) → 정상적으로 다름을 확인, 전처리 자체는 문제 없음
2. 모델의 raw softmax 출력을 직접 비교 → 서로 다른 이미지인데 소수점 4~5자리까지 동일 → 모델 입력 직전 단계 의심
3. `.h5` 파일을 `h5py`로 직접 열어 `model_config`에서 Lambda 레이어 확인 → `function: "preprocess_input"`으로 이름 참조되어 있음을 확인
4. `tensorflow.keras.applications.efficientnet.preprocess_input` 실제 소스 코드 확인 → identity 함수임을 확인
5. 커스텀 `preprocess_input`을 identity로 교체 + 0~255 원본 스케일 입력으로 재로드 후 예측 → 이미지마다 예측이 달라짐을 확인 (가설 검증 완료)

### 해결

`ai_model_service.py` 2곳 수정:

```python
# 1) 등록된 preprocess_input을 identity로 수정
@tf.keras.utils.register_keras_serializable()
def preprocess_input(x):
    return x  # 기존: return x / 255.0

# 2) predict_skin_type()에서 0~255 원본 스케일로 되돌려서 전달
input_array = np.expand_dims(image_array * 255.0, axis=0)  # 기존: image_array 그대로 사용
```

### 검증 (FFHQ 35장 기준, 수정 전 → 후)

| 지표 | 수정 전 | 수정 후 |
|:----|:-------|:-------|
| 타입 라벨 분포 | 지성 100% (전부 동일) | 지성 21 · 복합성 9 · 건성 5 |
| 타입 신뢰도 | 항상 35.8% (상수) | 36.9%~75.0% (평균 48.8%, 이미지마다 다름) |
| 저신뢰 비율(타입) | 100% | 88.6% |
| 설명 가능 비율 (구 게이트) | 0.0% | 5.7% |
| 설명 가능 비율 (신 게이트) | 80.0% | 80.0% (변화 없음 — 타입 신호를 애초에 배제하므로) |

**해석**: 타입 모델의 신뢰도가 낮은 건(저신뢰 비율 88.6%) 버그가 아니라, FFHQ가 학습 데이터(AI-Hub 한국인 피부 데이터)와
분포가 다른 unseen 셋이기 때문에 나타나는 자연스러운 일반화 격차로 판단됨. 다만 버그 수정 전에는
"모델이 이미지를 아예 못 보고 있었다"는 점에서 근본적으로 다른 문제였음.

---

## 2. 진단 신뢰성 안전장치 — 정량 평가

### 측정 지표 정의

- **모순율(self-contradiction rate)**: 질환 모델이 "정상"으로 판정했는데 상태 모델이 이상 소견을 70% 이상 신뢰도로
  탐지한 경우 (`uncertainty_detector.py`)
- **설명 가능 비율**: 근거(RAG) 기반 설명이 실제로 생성된 비율. "구 게이트"는 타입 포함 어떤 모델이든 저신뢰면 차단,
  "신 게이트"는 질환·상태 관련 신호만 반영 (안전 게이트 범위를 좁힌 버그 수정 — 별도 세션에서 진행)

### 결과 (버그 수정 후, FFHQ 35장)

| 지표 | 값 |
|:----|:--|
| 모순율 | 8.6% |
| 저신뢰 비율 — 피부 타입 | 88.6% |
| 저신뢰 비율 — 피부 질환 | 0.0% |
| 저신뢰 비율 — 피부 상태 | 11.4% |
| 설명 대상 케이스 | 35건 / 35건 |
| 설명 가능 비율 (구 게이트) | 5.7% |
| 설명 가능 비율 (신 게이트) | 80.0% |

### 해석

안전 게이트 범위를 "질환·상태 관련 신호만" 보도록 좁힌 수정이 실제로 설명 가능 비율을 5.7% → 80.0%로
끌어올렸음을 정량적으로 확인. 타입 모델의 구조적으로 낮은 신뢰도가 질환/상태 설명까지 막던 문제가
해소되었음을 숫자로 증명.

---

## 3. 배포 트러블슈팅 — RAG 추가로 인한 재발 OOM

### 증상
Cloud Run(메모리 2Gi)에 RAG+Groq 반영 후 재배포 → `/api/ai/analyze-skin` 요청 시 503 Service
Unavailable. 로그 확인 결과 YOLO/EfficientNet 추론까지는 정상 완료됐으나, RAG 검색을 위해
SentenceTransformer(`jhgan/ko-sroberta-multitask`) 임베딩 모델을 최초 로딩하는 시점 직후
로그가 끊기고 컨테이너가 처음부터 재시작(모델 로딩부터 재시작)되는 패턴 확인.

### 원인
TensorFlow(EfficientNet) + PyTorch(YOLOv8n ×2) + SentenceTransformer가 모두 하나의
컨테이너 메모리에 동시에 올라가면서 2Gi 한도 초과 → Cloud Run이 컨테이너를 OOM kill.
기존에도 동일 클래스의 문제(README 트러블슈팅 표: "런타임 크래시 OOM")가 있었는데,
RAG 의존성 추가로 재발한 것.

### 해결
`gcloud run services update skin-api --memory 4Gi`로 메모리를 2Gi → 4Gi 상향, 이미지 재빌드 없이
새 리비전만 배포. 이후 동일 이미지로 재요청 시 정상 응답 확인.

### 검증
라이브 URL에 실제 이미지 2장(근거 확인 케이스, 허용목록 제외 케이스)으로 재테스트 —
로컬 테스트와 동일한 응답 확인.

---

## 원자료

전체 이미지별 상세 결과: [`eval/results.json`](./results.json)
재실행 방법: `python eval/run_contradiction_eval.py` (skin_project 루트에서)
