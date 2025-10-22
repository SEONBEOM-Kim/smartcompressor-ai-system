#!/usr/bin/env python3
"""
Python 의존성 설치 스크립트
"""

import subprocess
import sys
import os

def install_package(package):
    """패키지 설치"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} 설치 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package} 설치 실패: {e}")
        return False

def main():
    """메인 설치 함수"""
    print("🐍 Python 의존성 설치 시작...")
    
    # 필수 패키지 목록
    packages = [
        "numpy",
        "scipy", 
        "soundfile",
        "librosa",
        "requests",
        "pathlib"
    ]
    
    success_count = 0
    total_count = len(packages)
    
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 설치 결과: {success_count}/{total_count} 패키지 성공")
    
    if success_count == total_count:
        print("🎉 모든 의존성 설치 완료!")
        return True
    else:
        print("⚠️ 일부 패키지 설치 실패. 수동으로 설치해주세요.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
