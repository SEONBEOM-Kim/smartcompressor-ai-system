#!/bin/bash
# GitHub Personal Access Token 설정 스크립트

echo "🔐 GitHub Personal Access Token 설정"
echo "=================================="

# .env 파일 생성
echo "📁 .env 파일 생성 중..."
cat > .env << EOF
# GitHub Personal Access Token
GITHUB_TOKEN=your_personal_access_token_here

# Git 사용자 정보
GIT_USER_NAME=your_username
GIT_USER_EMAIL=your_email@example.com

# 사용법:
# 1. 위의 값들을 실제 값으로 교체하세요
# 2. 이 파일은 .gitignore에 포함되어 Git에 커밋되지 않습니다
EOF

echo "✅ .env 파일이 생성되었습니다"
echo ""
echo "📝 다음 단계:"
echo "1. .env 파일을 열어서 실제 토큰과 사용자 정보를 입력하세요"
echo "2. 아래 명령어로 Git 원격 저장소를 설정하세요:"
echo ""
echo "   source .env"
echo "   git remote set-url origin https://\$GIT_USER_NAME:\$GITHUB_TOKEN@github.com/SEONBEOM-Kim/smartcompressor-ai-system.git"
echo ""
echo "3. 푸시 테스트:"
echo "   git push origin main"
echo ""
echo "⚠️  보안 주의: .env 파일은 절대 공유하지 마세요!"
