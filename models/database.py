import sqlite3
import os
from datetime import datetime

def init_db():
    """데이터베이스 초기화"""
    try:
        # 데이터베이스 파일 생성
        db_path = 'smartcompressor.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 사용자 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT,
                company TEXT,
                marketing_agree BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 세션 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("데이터베이스 초기화 완료")
        return True
        
    except Exception as e:
        print(f"데이터베이스 초기화 오류: {str(e)}")
        return False

def get_user_by_email(email):
    """이메일로 사용자 조회"""
    try:
        # 임시 사용자 조회
        if email == 'admin@signalcraft.kr':
            return {
                'id': 1,
                'email': 'admin@signalcraft.kr',
                'name': '관리자',
                'company': 'Signalcraft'
            }
        return None
    except Exception as e:
        return None

def create_user(email, password, name, phone=None, company=None, marketing_agree=False):
    """새 사용자 생성"""
    try:
        # 임시 사용자 생성
        return 1  # 임시 사용자 ID
    except Exception as e:
        return None
