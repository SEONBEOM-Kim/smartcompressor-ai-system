#!/bin/bash
# SSH 키 생성 및 설정 가이드

echo "🔑 SSH 키 생성 및 설정 가이드"
echo ""

# 1. SSH 키 생성
echo "1. SSH 키 생성 중..."
ssh-keygen -t rsa -b 4096 -f signalcraft_key -N ""

echo ""
echo "✅ SSH 키 생성 완료!"
echo ""

# 2. 공개키 내용 출력
echo "2. 공개키 내용 (EC2 서버에 추가해야 함):"
echo "----------------------------------------"
cat signalcraft_key.pub
echo "----------------------------------------"
echo ""

# 3. 개인키 내용 출력
echo "3. 개인키 내용 (GitHub Secrets에 추가해야 함):"
echo "----------------------------------------"
cat signalcraft_key
echo "----------------------------------------"
echo ""

echo "📋 다음 단계:"
echo "1. 공개키를 EC2 서버의 ~/.ssh/authorized_keys에 추가"
echo "2. 개인키를 GitHub Secrets의 EC2_SSH_KEY에 추가"
echo "3. GitHub Actions 재실행"
