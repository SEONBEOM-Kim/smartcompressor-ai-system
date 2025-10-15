# SignalCraft 데이터베이스 마이그레이션 가이드

이 문서는 SignalCraft 시스템의 SQLite 데이터베이스를 PostgreSQL로 마이그레이션하는 절차를 설명합니다.

## 개요

SignalCraft 시스템은 확장성과 동시성 문제를 해결하기 위해 SQLite에서 PostgreSQL로 데이터베이스를 마이그레이션합니다. 이 문서는 마이그레이션 절차와 관련 스크립트 사용법을 설명합니다.

## 사전 준비

1. PostgreSQL 서버 설치 및 실행
2. 마이그레이션 대상 데이터베이스 생성
3. 환경 변수 설정 (config/database.env 파일 참조)

## 설정 파일

`config/database.env` 파일에 다음 설정을 추가합니다:

```env
# SQLite (current)
DB_TYPE=sqlite
SQLITE_PATH=./database.db

# PostgreSQL (for migration)
DB_TYPE_NEW=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=signalcraft
DB_USER=signalcraft_user
DB_PASSWORD=your_secure_password

# Connection settings
DB_POOL_SIZE=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=3600

# Migration settings
BACKUP_PATH=./backups/
```

## 마이그레이션 실행

1. **백업 확인**: 마이그레이션 전에 기존 데이터베이스를 백업합니다.
2. **依존성 설치**:
   ```bash
   pip install -r requirements.txt
   ```
3. **마이그레이션 스크립트 실행**:
   ```bash
   python scripts/migrate_to_postgres.py
   ```
4. **결과 검증**: 마이그레이션 결과를 검증합니다.

## 주의사항

- 마이그레이션 도중 장애가 발생할 수 있으므로, 비즈니스 시간 외에 실행하는 것을 권장합니다.
- 마이그레이션 후에는 애플리케이션 설정을 변경하여 PostgreSQL을 사용하도록 해야 합니다.
- 마이그레이션 전후에 데이터가 정상적으로 이전되었는지 확인해야 합니다.

## 롤백 절차

마이그레이션 후 문제가 발생할 경우, 백업 파일을 사용하여 원래 SQLite 데이터베이스로 복구할 수 있습니다.

## 추가 도구

- `scripts/validate_migration.py`: 마이그레이션 후 데이터 무결성 검증
- `scripts/compare_performance.py`: SQLite와 PostgreSQL의 성능 비교