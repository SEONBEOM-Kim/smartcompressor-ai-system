# 🎵 AI 오디오 진단 시스템

산업용 압축기의 오디오 신호를 분석하여 이상 상태를 진단하는 AI 시스템입니다. 듀얼 마이크 환경을 시뮬레이션하고, 노이즈 제거, 전문가 라벨링, CNN 모델 훈련, 실시간 진단까지 전체 파이프라인을 제공합니다.

## 📋 시스템 구성

### 5개 핵심 Python 스크립트

1. **`data_collector.py`** - 데이터 수집 시뮬레이터
2. **`preprocessor.py`** - 1차 정제 및 증류 모듈  
3. **`labeling_tool.py`** - 전문가 라벨링 GUI
4. **`train_ai.py`** - AI 훈련 스크립트
5. **`run_diagnosis.py`** - 실시간 진단 스크립트

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# Python 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 2. 샘플 데이터 준비

```bash
# 샘플 오디오 파일 다운로드 (예시)
wget https://example.com/target_audio.wav
wget https://example.com/noise_audio.wav
```

### 3. 전체 파이프라인 실행

```bash
# 1단계: 데이터 수집
python data_collector.py --target target_audio.wav --noise noise_audio.wav

# 2단계: 전처리 및 스펙트로그램 생성
python preprocessor.py --target data/raw/target_with_noise_*.wav --noise data/raw/noise_only_*.wav

# 3단계: 전문가 라벨링 (웹 GUI)
streamlit run labeling_tool.py

# 4단계: AI 모델 훈련
python train_ai.py --data-dir labeled_data

# 5단계: 실시간 진단
python run_diagnosis.py --target new_target.wav --noise new_noise.wav
```

## 📁 디렉토리 구조

```
smartcompressor-ai-system/
├── data_collector.py          # 데이터 수집 시뮬레이터
├── preprocessor.py            # 전처리 모듈
├── labeling_tool.py           # 라벨링 GUI
├── train_ai.py               # AI 훈련
├── run_diagnosis.py          # 실시간 진단
├── requirements.txt          # Python 의존성
├── README.md                 # 이 파일
├── data/                     # 데이터 디렉토리
│   ├── raw/                  # 원시 오디오 데이터
│   ├── processed/            # 정제된 오디오
│   └── spectrograms/         # 스펙트로그램 이미지
├── labeled_data/             # 라벨링된 데이터
│   ├── normal/               # 정상 가동음
│   ├── leak/                 # 냉기 누설 신호
│   └── overload/             # 과부하 신호
├── models/                   # 훈련된 AI 모델
├── results/                  # 훈련 결과
└── diagnosis_results/        # 진단 결과
```

## 🔧 상세 사용법

### 1. data_collector.py - 데이터 수집 시뮬레이터

듀얼 마이크 환경을 시뮬레이션하여 오디오 데이터를 수집합니다.

```bash
# 기본 사용법
python data_collector.py --target target.wav --noise noise.wav

# 듀얼 마이크 시뮬레이션 사용
python data_collector.py --target target.wav --noise noise.wav --dual-mic --mic-distance 0.1

# 옵션 설명
--target          # 타겟 오디오 파일 경로
--noise           # 노이즈 오디오 파일 경로  
--output          # 출력 디렉토리 (기본값: data/raw)
--duration        # 수집할 오디오 길이 (초, 기본값: 5.0)
--sample-rate     # 샘플링 레이트 (기본값: 22050)
--dual-mic        # 듀얼 마이크 환경 시뮬레이션 사용
--mic-distance    # 마이크 간 거리 (미터, 기본값: 0.1)
```

**출력 파일:**
- `target_with_noise_YYYYMMDD_HHMMSS.wav` - 타겟 + 노이즈 합성 오디오
- `noise_only_YYYYMMDD_HHMMSS.wav` - 노이즈만 오디오

### 2. preprocessor.py - 전처리 모듈

노이즈 제거 및 스펙트로그램 생성을 수행합니다.

```bash
# 기본 사용법
python preprocessor.py --target target_with_noise.wav --noise noise_only.wav

# 다중 윈도우 크기로 스펙트로그램 생성
python preprocessor.py --target target.wav --noise noise.wav --multiple-windows --window-sizes 5.0 3.0 1.0

# 옵션 설명
--target              # 타겟 오디오 파일 경로
--noise               # 노이즈 오디오 파일 경로
--output-processed    # 정제된 오디오 출력 디렉토리 (기본값: data/processed)
--output-spectrograms # 스펙트로그램 출력 디렉토리 (기본값: data/spectrograms)
--image-size          # 이미지 크기 (기본값: 256 256)
--colormap            # 컬러맵 (기본값: magma)
--multiple-windows    # 다양한 윈도우 크기로 스펙트로그램 생성
--window-sizes        # 윈도우 크기들 (초)
```

**주요 기능:**
- **노이즈 제거**: 위상 반전 + 스펙트럼 차감 기법
- **스펙트로그램 생성**: 256x256 픽셀, magma 컬러맵
- **다중 윈도우**: 다양한 시간 윈도우로 분석

### 3. labeling_tool.py - 전문가 라벨링 GUI

Streamlit 기반의 웹 인터페이스로 스펙트로그램을 라벨링합니다.

```bash
# Streamlit 서버 시작
streamlit run labeling_tool.py

# 특정 디렉토리 지정
streamlit run labeling_tool.py -- --input-dir data/spectrograms

# 옵션 설명
--input-dir    # 라벨링할 스펙트로그램 디렉토리 (기본값: data/spectrograms)
--port         # 서버 포트 (기본값: 8501)
```

**라벨링 클래스:**
- **정상 가동음** (`normal`) - 정상적인 압축기 가동음
- **냉기 누설 신호** (`leak`) - 냉매 누설로 인한 이상 신호  
- **과부하 신호** (`overload`) - 과부하 상태의 이상 신호

**GUI 기능:**
- 진행 상황 실시간 표시
- 키보드 단축키 지원 (1, 2, 3, 스페이스바)
- 라벨링 히스토리 확인
- 이미지 건너뛰기 기능

### 4. train_ai.py - AI 훈련 스크립트

라벨링된 데이터로 CNN 모델을 훈련합니다.

```bash
# 기본 사용법
python train_ai.py

# 고급 옵션
python train_ai.py --data-dir labeled_data --epochs 100 --batch-size 64 --image-size 256 256

# 옵션 설명
--data-dir           # 라벨링된 데이터 디렉토리 (기본값: labeled_data)
--output-dir         # 모델 저장 디렉토리 (기본값: models)
--results-dir        # 결과 저장 디렉토리 (기본값: results)
--epochs             # 훈련 에포크 수 (기본값: 50)
--batch-size         # 배치 크기 (기본값: 32)
--image-size         # 이미지 크기 (기본값: 256 256)
--validation-split   # 검증 데이터 비율 (기본값: 0.2)
```

**모델 구조:**
- 4개 컨볼루션 블록 (32, 64, 128, 256 필터)
- 배치 정규화 및 드롭아웃
- 전역 평균 풀링
- 2개 완전 연결 레이어 (512, 256)
- 3개 클래스 출력 (정상, 누설, 과부하)

**출력 파일:**
- `models/model.h5` - 훈련된 모델
- `models/class_info.txt` - 클래스 정보
- `results/training_history_*.png` - 훈련 히스토리 그래프

### 5. run_diagnosis.py - 실시간 진단 스크립트

새로운 오디오 파일을 분석하여 AI 진단을 수행합니다.

```bash
# 기본 사용법
python run_diagnosis.py --target new_target.wav --noise new_noise.wav

# 상세 로그와 함께
python run_diagnosis.py --target target.wav --noise noise.wav --verbose

# 옵션 설명
--target    # 타겟 오디오 파일 경로 (필수)
--noise     # 노이즈 오디오 파일 경로 (필수)
--model     # 훈련된 모델 파일 경로 (기본값: models/model.h5)
--output    # 결과 저장 디렉토리 (기본값: diagnosis_results)
--verbose   # 상세 로그 출력
```

**진단 결과:**
- 예측된 클래스와 신뢰도
- 모든 클래스별 확률 분포
- 시각적 확률 바 차트
- 권장사항 및 조치 방안

## 📊 예제 출력

### 진단 결과 예시

```
============================================================
🔍 AI 오디오 진단 결과
============================================================
📅 진단 시간: 20241201_143022
📁 타겟 오디오: data/raw/target_with_noise_20241201_143000.wav
📁 노이즈 오디오: data/raw/noise_only_20241201_143000.wav

🎯 진단 결과:
   상태: 이상
   분류: 냉기 누설 신호
   신뢰도: 95.2%

📊 모든 클래스별 확률:
   냉기 누설 신호    : 95.2% ████████████████████
   과부하 신호      : 3.8%  ████░░░░░░░░░░░░░░░░
   정상 가동음      : 1.0%  █░░░░░░░░░░░░░░░░░░░

💡 권장사항:
   ⚠️ 냉매 누설이 의심됩니다.
   🔧 즉시 전문가에게 점검을 요청하세요.
   🚨 안전을 위해 압축기를 중단하는 것을 고려하세요.
============================================================
```

## 🛠️ 관리자 시스템

### 서비스 운영 관리 시스템
- **AWS Management Console & GitHub 벤치마킹**
- 매장 등록 및 승인 시스템
- 사용자 권한 및 역할 관리
- 서비스 상태 모니터링
- 로그 관리 및 분석
- 고객 지원 티켓 시스템
- 감사 로그 및 보안 관리
- 백업 및 복구 시스템
- 성능 모니터링 및 알림

### 접근 방법
```bash
# 관리자 대시보드
http://localhost:8000/admin
```

### 관리자 기능
- **매장 관리**: 매장 등록, 승인, 정지, 삭제
- **사용자 관리**: 사용자 생성, 권한 관리, 역할 할당
- **모니터링**: 서비스 상태, 시스템 메트릭, 실시간 모니터링
- **로그 관리**: 로그 조회, 내보내기, 정리
- **고객 지원**: 티켓 생성, 할당, 상태 관리
- **보안 관리**: 보안 이벤트, IP 차단, 감사 로그
- **백업 관리**: 백업 생성, 복원, 다운로드
- **성능 모니터링**: 성능 메트릭, 알림, 최적화

## 🛠️ 고급 설정

### 환경 변수 설정

```bash
# .env 파일 생성
echo "CUDA_VISIBLE_DEVICES=0" > .env
echo "TF_CPP_MIN_LOG_LEVEL=2" >> .env
```

### GPU 사용 설정

```python
# GPU 메모리 동적 할당
import tensorflow as tf
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    tf.config.experimental.set_memory_growth(gpus[0], True)
```

### 배치 처리

```bash
# 여러 파일 일괄 처리
for file in data/raw/target_*.wav; do
    python run_diagnosis.py --target "$file" --noise "${file/target/noise}"
done
```

## 🔍 문제 해결

### 일반적인 문제

1. **모델 파일을 찾을 수 없음**
   ```bash
   # 모델 훈련 먼저 실행
   python train_ai.py
   ```

2. **메모리 부족 오류**
   ```bash
   # 배치 크기 줄이기
   python train_ai.py --batch-size 16
   ```

3. **Streamlit 서버 시작 실패**
   ```bash
   # 포트 변경
   streamlit run labeling_tool.py --server.port 8502
   ```

4. **오디오 파일 로드 실패**
   ```bash
   # 파일 형식 확인
   file your_audio.wav
   ```

### 로그 확인

```bash
# 상세 로그와 함께 실행
python run_diagnosis.py --target target.wav --noise noise.wav --verbose
```

## 📈 성능 최적화

### 훈련 성능 향상

1. **데이터 증강 사용**
   - 이미지 회전, 이동, 확대/축소
   - 노이즈 추가, 밝기 조절

2. **하이퍼파라미터 튜닝**
   ```bash
   python train_ai.py --epochs 100 --batch-size 64 --learning-rate 0.0001
   ```

3. **조기 종료 사용**
   - 검증 손실이 10 에포크 동안 개선되지 않으면 훈련 중단

### 추론 성능 향상

1. **모델 양자화**
   ```python
   # TensorFlow Lite 변환
   converter = tf.lite.TFLiteConverter.from_keras_model(model)
   tflite_model = converter.convert()
   ```

2. **배치 처리**
   - 여러 파일을 한 번에 처리

## 🔧 확장 가능성

### 새로운 클래스 추가

1. `labeling_tool.py`에서 클래스 수정
2. `train_ai.py`에서 `num_classes` 업데이트
3. `run_diagnosis.py`에서 클래스 매핑 수정

### 다른 오디오 형식 지원

1. `preprocessor.py`에서 추가 형식 지원
2. `librosa`의 `load` 함수 옵션 수정

### 실시간 스트리밍

1. `run_diagnosis.py`를 웹 서비스로 변환
2. WebSocket을 통한 실시간 데이터 전송
3. 모바일 앱 연동

## 📚 참고 자료

- [Librosa 공식 문서](https://librosa.org/)
- [TensorFlow/Keras 가이드](https://www.tensorflow.org/guide/keras)
- [Streamlit 문서](https://docs.streamlit.io/)
- [산업용 오디오 분석 연구](https://example.com/research)

## 📄 라이선스

MIT License - 자세한 내용은 LICENSE 파일을 참조하세요.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해주세요.

---

**🎵 AI 오디오 진단 시스템으로 산업용 압축기의 건강 상태를 지켜보세요!**
