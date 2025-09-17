#!/bin/bash
# EC2 배포 상태 확인 스크립트

echo "🔍 SIGNALCRAFT EC2 배포 상태 확인"
echo "=================================="

# 1. 서비스 프로세스 확인
echo "📊 실행 중인 서비스:"
ps aux | grep -E "(node server.js|python.*web_app.py)" | grep -v grep

echo ""
echo "🌐 포트 사용 상태:"
netstat -tlnp | grep -E ":(3000|8001)"

echo ""
echo "🧪 API 테스트:"
echo "Node.js 서버 (포트 3000):"
curl -s http://localhost:3000/api/auth/verify || echo "❌ Node.js API 응답 없음"

echo ""
echo "Python 서버 (포트 8001):"
curl -s http://localhost:8001/ || echo "❌ Python API 응답 없음"

echo ""
echo "📝 최근 로그 (Node.js):"
tail -5 node_server.log 2>/dev/null || echo "로그 파일 없음"

echo ""
echo "📝 최근 로그 (Python):"
tail -5 /var/log/smartcompressor.log 2>/dev/null || echo "로그 파일 없음"

echo ""
echo "🎉 배포 상태 확인 완료!"
echo "🌐 Node.js 서버: http://3.39.124.0:3000"
echo "🐍 Python 서버: http://3.39.124.0:8001"
