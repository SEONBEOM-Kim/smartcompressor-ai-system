# SIGNALCRAFT EC2 배포 가이드

## 🚀 수동 배포 방법

### 1. EC2 서버에 SSH 접속
```bash
ssh -i your-key.pem ubuntu@3.39.124.0
```

### 2. 프로젝트 디렉토리로 이동
```bash
cd /home/ubuntu/smartcompressor-ai-system
```

### 3. 최신 코드 가져오기
```bash
git pull origin main
```

### 4. Node.js 의존성 설치
```bash
npm install
```

### 5. 기존 서비스 종료
```bash
pkill -f "node server.js"
pkill -f "node app.js"
```

### 6. 새 서비스 시작
```bash
nohup node server.js > server.log 2>&1 &
```

### 7. 서비스 상태 확인
```bash
# 프로세스 확인
ps aux | grep "node server.js"

# 로그 확인
tail -f server.log

# API 테스트
curl http://localhost:3000/api/auth/verify
```

## 🔧 GitHub Actions 자동 배포 설정

### 1. GitHub Secrets 설정
Repository Settings > Secrets and variables > Actions에서 다음 secrets 추가:

- `EC2_HOST`: `3.39.124.0`
- `EC2_USER`: `ubuntu`
- `EC2_SSH_KEY`: EC2 SSH 개인키 내용

### 2. 자동 배포 활성화
- main 브랜치에 push할 때마다 자동 배포
- 수동 배포도 가능 (Actions 탭에서 workflow_dispatch 실행)

## 📊 배포 후 확인사항

### 서비스 URL
- **메인 페이지**: http://3.39.124.0:3000
- **관리자 대시보드**: http://3.39.124.0:3000/admin
- **API 엔드포인트**: http://3.39.124.0:3000/api/*

### 주요 기능 테스트
1. **카카오 로그인**: 네비게이션 바의 노란색 버튼
2. **AI 진단**: 체험 모듈에서 녹음/분석
3. **관리자 기능**: /admin 경로 접속
4. **실시간 모니터링**: /api/monitoring/* 엔드포인트

## 🚨 문제 해결

### 서비스가 시작되지 않는 경우
```bash
# 로그 확인
tail -50 server.log

# 포트 사용 확인
netstat -tlnp | grep :3000

# Node.js 버전 확인
node --version
npm --version
```

### 메모리 부족 문제
```bash
# 메모리 사용량 확인
free -h

# 프로세스 정리
pkill -f node
```

### Git pull 실패
```bash
# Git 상태 확인
git status

# 강제 pull
git fetch origin
git reset --hard origin/main
```

## 📝 배포 체크리스트

- [ ] EC2 서버 접속 성공
- [ ] Git pull 성공
- [ ] npm install 성공
- [ ] 기존 서비스 종료
- [ ] 새 서비스 시작
- [ ] API 테스트 성공
- [ ] 웹사이트 접속 확인
- [ ] 카카오 로그인 테스트
- [ ] AI 진단 기능 테스트
