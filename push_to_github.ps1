# 자동 GitHub 푸시 스크립트 (PowerShell)

Write-Host "🚀 GitHub 자동 푸시 시작" -ForegroundColor Green

# .env 파일에서 환경 변수 로드
if (Test-Path ".env") {
    Write-Host "📁 .env 파일에서 환경 변수 로드 중..." -ForegroundColor Yellow
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
} else {
    Write-Host "❌ .env 파일을 찾을 수 없습니다. 먼저 setup_github_token.ps1을 실행하세요." -ForegroundColor Red
    exit 1
}

# 환경 변수 확인
if (-not $env:GITHUB_TOKEN -or $env:GITHUB_TOKEN -eq "your_personal_access_token_here") {
    Write-Host "❌ GITHUB_TOKEN이 설정되지 않았습니다. .env 파일을 확인하세요." -ForegroundColor Red
    exit 1
}

if (-not $env:GIT_USER_NAME -or $env:GIT_USER_NAME -eq "your_username") {
    Write-Host "❌ GIT_USER_NAME이 설정되지 않았습니다. .env 파일을 확인하세요." -ForegroundColor Red
    exit 1
}

# Git 원격 저장소 설정
Write-Host "🔧 Git 원격 저장소 설정 중..." -ForegroundColor Yellow
$remoteUrl = "https://$($env:GIT_USER_NAME):$($env:GITHUB_TOKEN)@github.com/SEONBEOM-Kim/smartcompressor-ai-system.git"
git remote set-url origin $remoteUrl

# 변경사항 추가
Write-Host "📝 변경사항 추가 중..." -ForegroundColor Yellow
git add .

# 커밋
$commitMessage = "자동 커밋: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "💾 커밋 중: $commitMessage" -ForegroundColor Yellow
git commit -m $commitMessage

# 푸시
Write-Host "🚀 GitHub에 푸시 중..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 푸시 성공!" -ForegroundColor Green
} else {
    Write-Host "❌ 푸시 실패. 오류를 확인하세요." -ForegroundColor Red
}
