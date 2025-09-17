# 카카오 로그인 API 키 설정 스크립트 (PowerShell)

Write-Host "🟡 카카오 로그인 API 키 설정" -ForegroundColor Yellow
Write-Host "==================================" -ForegroundColor Yellow

# 기존 .env 파일이 있는지 확인
if (Test-Path ".env") {
    Write-Host "📁 기존 .env 파일을 백업합니다..." -ForegroundColor Yellow
    Copy-Item ".env" ".env.backup"
    Write-Host "✅ .env.backup 파일로 백업 완료" -ForegroundColor Green
} else {
    Write-Host "📁 .env 파일이 없습니다. 새로 생성합니다..." -ForegroundColor Yellow
}

# 사용자 입력 받기
Write-Host ""
Write-Host "카카오 개발자 콘솔에서 API 키를 확인하세요: https://developers.kakao.com/" -ForegroundColor Cyan
Write-Host ""

$kakaoRestApiKey = Read-Host "카카오 REST API 키를 입력하세요"
$kakaoClientSecret = Read-Host "카카오 Client Secret을 입력하세요"
$redirectUri = Read-Host "리다이렉트 URI를 입력하세요 (기본값: http://localhost:8000/auth/kakao/callback)"

if ([string]::IsNullOrEmpty($redirectUri)) {
    $redirectUri = "http://localhost:8000/auth/kakao/callback"
}

# .env 파일에 카카오 설정 추가
Write-Host "📝 .env 파일에 카카오 설정을 추가합니다..." -ForegroundColor Yellow

$envContent = @"
# ===========================================
# 🔐 API 키 및 인증 정보 관리
# ===========================================

# GitHub Personal Access Token
GITHUB_TOKEN=your_personal_access_token_here

# Git 사용자 정보
GIT_USER_NAME=your_username
GIT_USER_EMAIL=your_email@example.com

# ===========================================
# 🟡 카카오 로그인 API 키
# ===========================================
KAKAO_REST_API_KEY=$kakaoRestApiKey
KAKAO_CLIENT_SECRET=$kakaoClientSecret
KAKAO_REDIRECT_URI=$redirectUri

# ===========================================
# 🔴 Flask 앱 설정
# ===========================================
FLASK_SECRET_KEY=your_flask_secret_key_here
FLASK_DEBUG=True
FLASK_PORT=8000

# ===========================================
# 🟣 데이터베이스 설정
# ===========================================
DATABASE_URL=sqlite:///smartcompressor.db

# ===========================================
# 사용법:
# 1. 위의 값들을 실제 값으로 교체하세요
# 2. 이 파일은 .gitignore에 포함되어 Git에 커밋되지 않습니다
"@

$envContent | Out-File -FilePath ".env" -Encoding UTF8

Write-Host "✅ 카카오 로그인 설정이 완료되었습니다!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 다음 단계:" -ForegroundColor Cyan
Write-Host "1. .env 파일을 확인하여 다른 필요한 설정도 추가하세요"
Write-Host "2. Flask 앱에서 환경 변수를 사용하세요:"
Write-Host "   import os"
Write-Host "   kakao_key = os.getenv('KAKAO_REST_API_KEY')"
Write-Host ""
Write-Host "보안 주의: .env 파일은 절대 공유하지 마세요!" -ForegroundColor Red
