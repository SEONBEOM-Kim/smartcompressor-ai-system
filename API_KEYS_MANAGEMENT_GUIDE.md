# 🔐 API 키 관리 가이드

## 📋 개요
이 가이드는 프로젝트에서 사용하는 모든 API 키들을 안전하게 관리하는 방법을 설명합니다.

## 🎯 장점

### ✅ 한 곳에서 모든 API 키 관리
- `.env` 파일 하나에서 모든 API 키 확인 가능
- 새로운 API 키 추가 시 한 곳만 수정하면 됨
- 팀원들과 설정 공유 시 `.env` 파일만 공유하면 됨

### ✅ 보안성
- `.gitignore`에 포함되어 Git에 커밋되지 않음
- 코드에 하드코딩되지 않음
- 환경별로 다른 설정 파일 사용 가능

### ✅ 편의성
- 자동화 스크립트로 쉽게 설정
- 환경 변수로 코드에서 간단히 사용
- 설정 검증 기능 제공

## 🚀 사용 방법

### 1단계: API 키 템플릿 복사
```powershell
# PowerShell에서 실행
copy api_keys_template.env .env
```

### 2단계: .env 파일 편집
```bash
# .env 파일을 열어서 실제 값으로 교체
KAKAO_REST_API_KEY=실제_카카오_API_키
KAKAO_CLIENT_SECRET=실제_카카오_시크릿_키
# ... 기타 필요한 API 키들
```

### 3단계: 자동 설정 스크립트 사용
```powershell
# 카카오 로그인 설정
.\setup_kakao_login.ps1

# GitHub 토큰 설정
.\setup_github_token.ps1
```

## 📁 포함된 API 키들

### 🔐 인증 관련
- **GitHub**: Personal Access Token
- **카카오**: REST API Key, Client Secret
- **네이버**: Client ID, Client Secret (선택사항)
- **구글**: Client ID, Client Secret (선택사항)

### 🗄️ 데이터베이스
- **SQLite/PostgreSQL**: Database URL

### 🤖 AI/ML
- **모델 경로**: AI 모델 및 특성 파일 경로

### 📧 통신
- **SMTP**: 이메일 발송 설정
- **Slack**: 웹훅 알림 설정

### 💳 결제
- **토스페이먼츠**: Secret Key, Client Key

## 💻 코드에서 사용하는 방법

### Python에서 환경 변수 사용
```python
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# API 키 사용
kakao_key = os.getenv('KAKAO_REST_API_KEY')
github_token = os.getenv('GITHUB_TOKEN')
```

### Flask 앱에서 사용
```python
from flask import Flask
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['KAKAO_REST_API_KEY'] = os.getenv('KAKAO_REST_API_KEY')
```

### 설정 검증
```python
# examples/env_usage_example.py 실행
python examples/env_usage_example.py
```

## 🔒 보안 주의사항

### ❌ 절대 하지 말아야 할 것들
1. **Git에 .env 파일 커밋하지 마세요**
2. **코드에 API 키를 하드코딩하지 마세요**
3. **공개 저장소에 API 키를 노출하지 마세요**
4. **.env 파일을 공유할 때는 실제 키를 제거하고 공유하세요**

### ✅ 안전한 관리 방법
1. **.env 파일은 로컬에서만 사용**
2. **팀원들과는 .env.template 파일 공유**
3. **프로덕션 환경에서는 별도 설정 파일 사용**
4. **정기적으로 API 키 갱신**

## 🛠️ 문제 해결

### 환경 변수가 로드되지 않는 경우
```python
# python-dotenv 설치 확인
pip install python-dotenv

# .env 파일 경로 확인
import os
print(os.path.exists('.env'))
```

### API 키가 None으로 나오는 경우
1. `.env` 파일에 해당 키가 있는지 확인
2. 키 이름이 정확한지 확인 (대소문자 구분)
3. `.env` 파일이 프로젝트 루트에 있는지 확인

### Git에 .env 파일이 커밋된 경우
```bash
# .env 파일을 Git에서 제거
git rm --cached .env

# .gitignore에 .env 추가 확인
echo ".env" >> .gitignore

# 커밋
git add .gitignore
git commit -m "Remove .env from tracking"
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. `.env` 파일이 프로젝트 루트에 있는지
2. `python-dotenv` 패키지가 설치되어 있는지
3. API 키 이름이 정확한지
4. `.gitignore`에 `.env`가 포함되어 있는지
