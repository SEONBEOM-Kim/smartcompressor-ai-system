# 🚀 SignalCraft 백엔드 진행 상황 및 현재 아키텍처 (beprogress.md)

> 이 문서는 최근 진행된 백엔드 개선 작업(PM2 통합, DB 마이그레이션)을 반영한 현재 아키텍처 상태를 기록하고, 다음 개발 단계를 명확히 하기 위해 작성되었습니다.

---

## 1. 현재 백엔드 아키텍처 다이어그램

현재 우리 시스템은 Nginx를 통해 요청을 받아 Node.js와 Python 백엔드로 분기하며, 두 백엔드 모두 **하나의 AWS RDS (PostgreSQL) 데이터베이스**를 바라보는 구조로 업데이트되었습니다.

```mermaid
graph TD
    subgraph "인프라 (AWS EC2)"
        A[Client/User] --> B(Nginx Reverse Proxy);
        B --> C{Node.js (Express)};
        B --> D{Python (Flask + Gunicorn)};
        C --> E[AWS RDS for PostgreSQL];
        D --> E;
    end

    style C fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#ccf,stroke:#333,stroke-width:2px
    style E fill:#f8f,stroke:#333,stroke-width:4px
```

---

## 2. 프로세스 관리: PM2 통합 완료

`ecosystem.config.js`를 통해 Node.js와 Python(Flask) 두 프로세스를 **PM2로 통합 관리**하는 1차 목표를 달성했습니다.

- **Node.js 서버**: `cluster` 모드로 실행되어 CPU 코어를 모두 활용, 성능을 극대화합니다.
- **Python 서버**: `fork` 모드와 `Gunicorn`을 함께 사용하여 안정적으로 실행됩니다.

#### `ecosystem.config.js` 설정 요약

```javascript
module.exports = {
  apps: [
    {
      name: 'signalcraft-nodejs',
      script: 'server.js',
      exec_mode: 'cluster', // 클러스터 모드
      instances: 'max',
      // ...
    },
    {
      name: 'signalcraft-python',
      script: 'gunicorn', // Gunicorn으로 실행
      args: '-c gunicorn.conf.py app:app',
      exec_mode: 'fork',
      // ...
    }
  ]
};
```

---

## 3. 데이터베이스: PostgreSQL 마이그레이션 진행 중

**핵심 목표**: 기존의 로컬 SQLite에서 AWS RDS (PostgreSQL)로 전환하는 작업을 진행 중입니다.

#### ✅ 완료된 작업

1.  **`.env` 파일 통합**: 프로젝트 루트(`.env`)에 AWS RDS 연결 정보를 통합하여 Node.js와 Python이 모두 참조하도록 설정했습니다.

2.  **Python 연결 수정 (`service_monitoring_service.py`)**: 서비스 모니터링 시스템이 RDS 연결 상태를 직접 확인하도록 수정했습니다.

3.  **Node.js 연결 수정 (`database_service.js`)**: 
    - `.env` 파일을 참조하여 RDS에 연결하도록 설정했습니다.
    - 네트워크 지연을 고려하여 **연결 타임아웃을 10초로 늘렸습니다.**

---

## 4. 다음 개발 단계 추천

1.  **<del>[긴급] SQLite 잔여 로직 완전 제거</del> (완료)**
    - **~~목표~~**: ~~"SQLite 데이터베이스 연결 성공" 로그를 발생시키는 코드를 찾아 완전히 제거합니다.~~
    - **~~방법~~**: ~~프로젝트 전체에서 해당 문자열을 검색하여 원인 파일을 찾고, 관련 코드를 삭제하거나 주석 처리해야 합니다.~~
    - **~~기대 효과~~**: ~~불필요한 DB 연결을 막고, PostgreSQL로의 마이그레이션을 완전히 마무리합니다.~~

2.  **[신규] Python 서비스용 중앙 DB 모듈 생성 및 적용**
    - **목표**: 모든 Python 서비스가 단일 연결 포인트를 통해 AWS RDS (PostgreSQL)에 접속하도록 중앙 데이터베이스 모듈을 구현합니다.
    - **방법**:
        - `database.py`와 같은 중앙 모듈을 생성하여 PostgreSQL 연결 풀을 관리합니다.
        - 각 Python 서비스(`services/*.py`)가 이 모듈을 통해 DB 연결을 얻도록 수정합니다.
        - 주석 처리된 기존 SQLite 쿼리를 PostgreSQL 문법에 맞게 변환하여 각 서비스의 DB 관련 메서드를 재구현합니다.

3.  **[신규] JavaScript 서비스 DB 연결 통일**
    - **목표**: `data/labeling_database.js`가 중앙 `database_service.js`를 사용하도록 리팩토링합니다.
    - **방법**:
        - `labeling_database.js`에서 `database_service.js`를 `require`하여 DB 연결을 가져옵니다.
        - 주석 처리된 SQLite 쿼리를 PostgreSQL 문법에 맞게 변환하고 메서드를 재구현합니다.

4.  **[확인] AWS RDS 보안 그룹 점검**
    - **목표**: `connection timeout` 오류의 근본 원인이었던 보안 그룹 설정을 확인합니다.
    - **방법**: AWS 콘솔에 로그인하여 RDS 인스턴스의 보안 그룹이 EC2 인스턴스로부터의 5432 포트 인바운드 트래픽을 허용하는지 명확히 확인해야 합니다.

---

## 5. SQLite 로직 제거 작업 완료 (2025-10-15)

`suggestion.md` 파일에 명시된 모든 서비스 파일에서 SQLite 관련 로직을 성공적으로 제거했습니다.

- **작업 내용**:
    - `sqlite3` 모듈 import 구문 제거
    - 각 서비스의 생성자(`__init__`)에서 데이터베이스 경로 및 연결 객체 초기화 코드 제거
    - 데이터베이스를 초기화하는 `_init_database` 또는 `init_database` 메서드 전체 주석 처리
    - SQLite 데이터베이스와 직접 상호작용하던 모든 메서드들의 내부 로직을 주석 처리하고, PostgreSQL 구현이 필요하다는 경고 로그와 함께 기본값을 반환하도록 수정

- **적용된 파일**:
    - `services/ab_testing_service.py`
    - `services/advanced_analytics_service.py`
    - `services/customer_analytics_service.py`
    - `services/notification_management_service.py`
    - `services/offline_sync_service.py`
    - `services/product_catalog_service.py`
    - `services/sensor_data_service.py`
    - `services/sensor_database_service.py`
    - `services/store_management_service.py`
    - `data/labeling_database.js`

- **기대 효과**:
    - 모든 서비스에서 SQLite에 대한 직접적인 의존성 제거 완료
    - 향후 PostgreSQL로의 마이그레이션을 위한 기반 마련 (기존 로직을 주석으로 남겨두어 참고 가능)