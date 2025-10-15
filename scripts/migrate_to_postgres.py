#!/usr/bin/env python3
"""
SignalCraft 데이터베이스 마이그레이션 스크립트
SQLite에서 PostgreSQL로 데이터 마이그레이션을 수행합니다.
"""

import os
import sqlite3
import psycopg2
from dotenv import load_dotenv
import json
from datetime import datetime


def load_db_config():
    """환경 변수에서 데이터베이스 설정 로드"""
    load_dotenv('./config/database.env')
    
    config = {
        # SQLite (소스)
        'sqlite_path': os.getenv('SQLITE_PATH', './database.db'),
        
        # PostgreSQL (타겟)
        'pg_host': os.getenv('DB_HOST', 'localhost'),
        'pg_port': int(os.getenv('DB_PORT', 5432)),
        'pg_dbname': os.getenv('DB_NAME', 'signalcraft'),
        'pg_user': os.getenv('DB_USER', 'signalcraft_user'),
        'pg_password': os.getenv('DB_PASSWORD', 'your_secure_password')
    }
    
    return config


def connect_to_sqlite(db_path):
    """SQLite 데이터베이스 연결"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # 열 이름으로 접근 가능하게 함
    return conn


def connect_to_postgres(config):
    """PostgreSQL 데이터베이스 연결"""
    conn = psycopg2.connect(
        host=config['pg_host'],
        port=config['pg_port'],
        database=config['pg_dbname'],
        user=config['pg_user'],
        password=config['pg_password']
    )
    return conn


def get_table_names_sqlite(sqlite_conn):
    """SQLite 데이터베이스의 모든 테이블 이름 가져오기"""
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    return tables


def create_table_postgres(pg_conn, table_name, sqlite_conn):
    """PostgreSQL에 테이블 생성 (SQLite 테이블 구조 기반)"""
    cursor = sqlite_conn.cursor()
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    create_sql = cursor.fetchone()
    
    if create_sql:
        # SQLite SQL을 PostgreSQL 호환으로 변환
        pg_sql = create_sql[0].replace('AUTOINCREMENT', 'SERIAL')
        pg_sql = pg_sql.replace('INTEGER PRIMARY KEY', 'SERIAL PRIMARY KEY')
        
        pg_cursor = pg_conn.cursor()
        pg_cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")
        pg_cursor.execute(pg_sql)
        pg_conn.commit()
        print(f"Created table {table_name} in PostgreSQL")


def migrate_table_data(sqlite_conn, pg_conn, table_name):
    """지정된 테이블의 데이터를 SQLite에서 PostgreSQL로 마이그레이션"""
    # SQLite에서 데이터 가져오기
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute(f"SELECT * FROM {table_name};")
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        print(f"No data in table {table_name}")
        return
    
    # 열 이름 가져오기
    column_names = [description[0] for description in sqlite_cursor.description]
    placeholders = ', '.join(['%s'] * len(column_names))
    columns = ', '.join(column_names)
    
    # PostgreSQL에 데이터 삽입
    pg_cursor = pg_conn.cursor()
    insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"
    
    # 데이터 변환 (필요한 경우)
    converted_rows = []
    for row in rows:
        converted_row = []
        for i, value in enumerate(row):
            # JSON 데이터 처리
            if isinstance(value, str):
                try:
                    # JSON 문자열인지 확인
                    json.loads(value)
                    converted_row.append(value)
                except ValueError:
                    # JSON이 아니면 그대로 사용
                    converted_row.append(value)
            else:
                converted_row.append(value)
        converted_rows.append(converted_row)
    
    pg_cursor.executemany(insert_sql, converted_rows)
    pg_conn.commit()
    
    print(f"Migrated {len(rows)} rows to table {table_name}")


def backup_sqlite_db(sqlite_path, backup_path):
    """SQLite 데이터베이스 백업"""
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = os.path.join(backup_path, f"sqlite_backup_{timestamp}.db")
    
    # 백업 디렉토리 생성
    os.makedirs(backup_path, exist_ok=True)
    
    # 파일 복사
    shutil.copy2(sqlite_path, backup_filename)
    print(f"SQLite database backed up to {backup_filename}")
    
    return backup_filename


def validate_migration(sqlite_conn, pg_conn):
    """마이그레이션 검증 - 테이블 수와 행 수 비교"""
    print("Validating migration...")
    
    # SQLite 테이블 정보
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    sqlite_tables = [row[0] for row in sqlite_cursor.fetchall()]
    
    # PostgreSQL 테이블 정보
    pg_cursor = pg_conn.cursor()
    pg_cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public';
    """)
    pg_tables = [row[0] for row in pg_cursor.fetchall()]
    
    print(f"SQLite tables: {len(sqlite_tables)}")
    print(f"PostgreSQL tables: {len(pg_tables)}")
    
    # 각 테이블의 행 수 비교
    for table in sqlite_tables:
        if table in pg_tables:
            # SQLite 행 수
            sqlite_cursor.execute(f"SELECT COUNT(*) FROM {table};")
            sqlite_count = sqlite_cursor.fetchone()[0]
            
            # PostgreSQL 행 수
            pg_cursor.execute(f"SELECT COUNT(*) FROM {table};")
            pg_count = pg_cursor.fetchone()[0]
            
            print(f"Table {table}: SQLite={sqlite_count}, PostgreSQL={pg_count}")
            
            if sqlite_count != pg_count:
                print(f"⚠️  Mismatch in table {table}: {sqlite_count} != {pg_count}")
        else:
            print(f"⚠️  Table {table} missing in PostgreSQL")


def main():
    print("=== SignalCraft Database Migration Tool ===")
    print(f"Started at: {datetime.now()}")
    
    # 설정 로드
    config = load_db_config()
    print(f"Configuration loaded:")
    print(f"  SQLite: {config['sqlite_path']}")
    print(f"  PostgreSQL: {config['pg_host']}:{config['pg_port']}/{config['pg_dbname']}")
    
    # 백업 생성
    print("\n1. Creating backup of SQLite database...")
    backup_path = os.getenv('BACKUP_PATH', './backups/')
    backup_file = backup_sqlite_db(config['sqlite_path'], backup_path)
    
    # 연결
    print("\n2. Connecting to databases...")
    sqlite_conn = connect_to_sqlite(config['sqlite_path'])
    pg_conn = connect_to_postgres(config)
    
    try:
        # 테이블 목록 가져오기
        print("\n3. Discovering tables...")
        table_names = get_table_names_sqlite(sqlite_conn)
        print(f"Found tables: {table_names}")
        
        # PostgreSQL에 테이블 생성
        print("\n4. Creating tables in PostgreSQL...")
        for table_name in table_names:
            if table_name != 'sqlite_sequence':  # 시퀀스 테이블은 제외
                create_table_postgres(pg_conn, table_name, sqlite_conn)
        
        # 데이터 마이그레이션
        print("\n5. Migrating table data...")
        for table_name in table_names:
            if table_name != 'sqlite_sequence':  # 시퀀스 테이블은 제외
                print(f"Migrating table: {table_name}")
                migrate_table_data(sqlite_conn, pg_conn, table_name)
        
        # 마이그레이션 검증
        print("\n6. Validating migration...")
        validate_migration(sqlite_conn, pg_conn)
        
        print(f"\n✅ Migration completed at: {datetime.now()}")
        print("Note: Please review the migrated data before switching your application to PostgreSQL.")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise
    finally:
        sqlite_conn.close()
        pg_conn.close()


if __name__ == "__main__":
    main()