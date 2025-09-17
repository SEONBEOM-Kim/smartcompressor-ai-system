# GitHub Personal Access Token 설정 스크립트 (PowerShell)

Write-Host "🔐 GitHub Personal Access Token 설정" -ForegroundColor Green
Write-Host "==================================" -ForegroundColor Green

# .env 파일 생성
Write-Host "📁 .env 파일 생성 중..." -ForegroundColor Yellow
@"
# GitHub Personal Access Token
GITHUB_TOKEN=your_personal_access_token_here

# Git 사용자 정보
GIT_USER_NAME=your_username
GIT_USER_EMAIL=your_email@example.com

# 사용법:
# 1. 위의 값들을 실제 값으로 교체하세요
# 2. 이 파일은 .gitignore에 포함되어 Git에 커밋되지 않습니다
"@ | Out-File -FilePath ".env" -Encoding UTF8

Write-Host "✅ .env 파일이 생성되었습니다" -ForegroundColor Green
Write-Host ""
Write-Host "📝 다음 단계:" -ForegroundColor Cyan
Write-Host "1. .env 파일을 열어서 실제 토큰과 사용자 정보를 입력하세요"
Write-Host "2. 아래 명령어로 Git 원격 저장소를 설정하세요:"
Write-Host ""
Write-Host "   `$env:GITHUB_TOKEN = 'your_token_here'"
Write-Host "   `$env:GIT_USER_NAME = 'your_username'"
Write-Host "   git remote set-url origin https://`$env:GIT_USER_NAME`:`$env:GITHUB_TOKEN@github.com/SEONBEOM-Kim/smartcompressor-ai-system.git"
Write-Host ""
Write-Host "3. 푸시 테스트:"
Write-Host "   git push origin main"
Write-Host ""
Write-Host "⚠️  보안 주의: .env 파일은 절대 공유하지 마세요!" -ForegroundColor Red
