# 🔐 GitHub Personal Access Token 저장 및 사용 가이드

## 📋 개요
이 가이드는 GitHub Personal Access Token을 안전하게 저장하고 사용하는 방법을 설명합니다.

## 🚀 빠른 시작

### 1단계: 토큰 설정 스크립트 실행
```powershell
# PowerShell에서 실행
.\setup_github_token.ps1
```

### 2단계: .env 파일 편집
생성된 `.env` 파일을 열어서 실제 값으로 교체:
```
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
GIT_USER_NAME=your_actual_username
GIT_USER_EMAIL=your_actual_email@example.com
```

### 3단계: 자동 푸시 테스트
```powershell
# 자동 푸시 스크립트 실행
.\push_to_github.ps1
```

## 📁 생성되는 파일들

- `.env` - 환경 변수 파일 (Git에 커밋되지 않음)
- `github_token_setup.md` - 상세 설정 가이드
- `setup_github_token.ps1` - 토큰 설정 스크립트
- `push_to_github.ps1` - 자동 푸시 스크립트

## 🔒 보안 주의사항

1. **절대 Git에 토큰을 커밋하지 마세요**
2. `.env` 파일은 `.gitignore`에 포함되어 있습니다
3. 토큰을 공유하거나 공개하지 마세요
4. 정기적으로 토큰을 갱신하세요

## 🛠️ 수동 설정 방법

### Git 원격 저장소 수동 설정
```powershell
# 환경 변수 설정
$env:GITHUB_TOKEN = "your_token_here"
$env:GIT_USER_NAME = "your_username"

# 원격 저장소 설정
git remote set-url origin https://$env:GIT_USER_NAME:$env:GITHUB_TOKEN@github.com/SEONBEOM-Kim/smartcompressor-ai-system.git

# 푸시 테스트
git push origin main
```

## 🔧 문제 해결

### 토큰 권한 오류
- GitHub에서 토큰 권한을 확인하세요
- `repo` 권한이 활성화되어 있는지 확인하세요

### 인증 실패
- 토큰이 올바른지 확인하세요
- 사용자명이 정확한지 확인하세요

### 네트워크 오류
- 인터넷 연결을 확인하세요
- 방화벽 설정을 확인하세요

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. `.env` 파일의 값이 올바른지
2. GitHub 토큰이 유효한지
3. 저장소 권한이 있는지
