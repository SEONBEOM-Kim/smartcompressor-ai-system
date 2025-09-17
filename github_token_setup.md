# GitHub Personal Access Token 설정 가이드

## 🔐 Personal Access Token 생성 방법

1. GitHub에 로그인
2. Settings → Developer settings → Personal access tokens → Tokens (classic)
3. "Generate new token" 클릭
4. 토큰 이름: "smartcompressor-ai-system"
5. 권한 선택:
   - repo (전체 저장소 접근)
   - workflow (GitHub Actions 워크플로우)
6. "Generate token" 클릭
7. **토큰을 복사하여 안전한 곳에 저장** (한 번만 표시됨)

## 📁 토큰 저장 방법

### 방법 1: 환경 변수 파일 (권장)
```bash
# .env 파일 생성
echo "GITHUB_TOKEN=your_token_here" > .env
echo "GIT_USER_NAME=your_username" >> .env
echo "GIT_USER_EMAIL=your_email@example.com" >> .env
```

### 방법 2: Git 자격 증명 저장소
```bash
# Git 자격 증명 저장소에 저장
git config --global credential.helper store
```

### 방법 3: 별도 보안 파일
```bash
# 홈 디렉토리에 보안 파일 생성
echo "your_token_here" > ~/.github_token
chmod 600 ~/.github_token
```

## 🚀 Git 원격 저장소 설정

### HTTPS 방식 (토큰 사용)
```bash
git remote set-url origin https://your_username:your_token@github.com/SEONBEOM-Kim/smartcompressor-ai-system.git
```

### SSH 방식 (SSH 키 사용)
```bash
git remote set-url origin git@github.com:SEONBEOM-Kim/smartcompressor-ai-system.git
```

## ⚠️ 보안 주의사항

1. **절대 Git에 토큰을 커밋하지 마세요**
2. `.env` 파일은 `.gitignore`에 추가되어 있습니다
3. 토큰을 공유하거나 공개하지 마세요
4. 정기적으로 토큰을 갱신하세요

## 🔧 자동화 스크립트

토큰을 사용한 자동 푸시 스크립트를 만들 수 있습니다:

```bash
#!/bin/bash
# push_to_github.sh

# .env 파일에서 토큰 읽기
source .env

# Git 원격 저장소 설정
git remote set-url origin https://$GIT_USER_NAME:$GITHUB_TOKEN@github.com/SEONBEOM-Kim/smartcompressor-ai-system.git

# 변경사항 커밋 및 푸시
git add .
git commit -m "자동 커밋: $(date)"
git push origin main
```
