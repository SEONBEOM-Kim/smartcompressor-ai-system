#!/usr/bin/env python3
"""
매장 등록 및 관리 서비스
Tesla App 스타일의 매장 관리 시스템
"""

import time
import logging
import hashlib
import uuid
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from sqlite3 import connect
import json
import re

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StoreStatus(Enum):
    """매장 상태 열거형"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    SUSPENDED = "suspended"

class StoreType(Enum):
    """매장 유형 열거형"""
    FRANCHISE = "franchise"
    CORPORATE = "corporate"
    PARTNER = "partner"
    TEST = "test"

class DeviceStatus(Enum):
    """디바이스 상태 열거형"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"

@dataclass
class Store:
    """매장 정보"""
    store_id: str
    store_name: str
    store_type: StoreType
    owner_id: str
    address: str
    city: str
    state: str
    zip_code: str
    country: str
    phone: str
    email: str
    status: StoreStatus
    created_at: str
    updated_at: str
    last_activity: str
    settings: Dict

@dataclass
class StoreDevice:
    """매장 디바이스 정보"""
    device_id: str
    store_id: str
    device_name: str
    device_type: str  # compressor, sensor, etc.
    model: str
    serial_number: str
    status: DeviceStatus
    installed_at: str
    last_maintenance: str
    next_maintenance: str
    warranty_expires: str
    settings: Dict

@dataclass
class StoreMetrics:
    """매장 메트릭"""
    store_id: str
    total_devices: int
    online_devices: int
    offline_devices: int
    maintenance_devices: int
    error_devices: int
    total_energy_consumption: float
    energy_cost: float
    uptime_percentage: float
    alert_count: int
    last_updated: str

class StoreManagementService:
    """매장 등록 및 관리 서비스 (Tesla App 스타일)"""
    
    def __init__(self, db_path: str = 'data/store_management.db'):
        self.db_path = db_path
        self.stores = {}
        self.devices = {}
        self.metrics_cache = {}
        
        # 데이터베이스 초기화
        self._init_database()
        
        # 기존 데이터 로드
        self._load_stores()
        self._load_devices()
        
        logger.info("매장 관리 서비스 초기화 완료")
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 매장 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stores (
                        store_id TEXT PRIMARY KEY,
                        store_name TEXT NOT NULL,
                        store_type TEXT NOT NULL,
                        owner_id TEXT NOT NULL,
                        address TEXT NOT NULL,
                        city TEXT NOT NULL,
                        state TEXT NOT NULL,
                        zip_code TEXT NOT NULL,
                        country TEXT NOT NULL,
                        phone TEXT NOT NULL,
                        email TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        last_activity TEXT,
                        settings TEXT DEFAULT '{}'
                    )
                ''')
                
                # 매장 디바이스 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS store_devices (
                        device_id TEXT PRIMARY KEY,
                        store_id TEXT NOT NULL,
                        device_name TEXT NOT NULL,
                        device_type TEXT NOT NULL,
                        model TEXT NOT NULL,
                        serial_number TEXT NOT NULL,
                        status TEXT NOT NULL,
                        installed_at TEXT NOT NULL,
                        last_maintenance TEXT,
                        next_maintenance TEXT,
                        warranty_expires TEXT,
                        settings TEXT DEFAULT '{}',
                        FOREIGN KEY (store_id) REFERENCES stores (store_id)
                    )
                ''')
                
                # 매장 메트릭 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS store_metrics (
                        store_id TEXT PRIMARY KEY,
                        total_devices INTEGER DEFAULT 0,
                        online_devices INTEGER DEFAULT 0,
                        offline_devices INTEGER DEFAULT 0,
                        maintenance_devices INTEGER DEFAULT 0,
                        error_devices INTEGER DEFAULT 0,
                        total_energy_consumption REAL DEFAULT 0,
                        energy_cost REAL DEFAULT 0,
                        uptime_percentage REAL DEFAULT 0,
                        alert_count INTEGER DEFAULT 0,
                        last_updated TEXT NOT NULL,
                        FOREIGN KEY (store_id) REFERENCES stores (store_id)
                    )
                ''')
                
                # 인덱스 생성
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_stores_owner ON stores(owner_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_stores_status ON stores(status)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_devices_store ON store_devices(store_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_devices_status ON store_devices(status)')
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
    
    def _load_stores(self):
        """매장 데이터 로드"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM stores')
                
                for row in cursor.fetchall():
                    store = Store(
                        store_id=row[0],
                        store_name=row[1],
                        store_type=StoreType(row[2]),
                        owner_id=row[3],
                        address=row[4],
                        city=row[5],
                        state=row[6],
                        zip_code=row[7],
                        country=row[8],
                        phone=row[9],
                        email=row[10],
                        status=StoreStatus(row[11]),
                        created_at=row[12],
                        updated_at=row[13],
                        last_activity=row[14] or row[12],
                        settings=json.loads(row[15]) if row[15] else {}
                    )
                    
                    self.stores[store.store_id] = store
                
                logger.info(f"매장 데이터 로드 완료: {len(self.stores)}개")
                
        except Exception as e:
            logger.error(f"매장 데이터 로드 실패: {e}")
    
    def _load_devices(self):
        """디바이스 데이터 로드"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM store_devices')
                
                for row in cursor.fetchall():
                    device = StoreDevice(
                        device_id=row[0],
                        store_id=row[1],
                        device_name=row[2],
                        device_type=row[3],
                        model=row[4],
                        serial_number=row[5],
                        status=DeviceStatus(row[6]),
                        installed_at=row[7],
                        last_maintenance=row[8] or '',
                        next_maintenance=row[9] or '',
                        warranty_expires=row[10] or '',
                        settings=json.loads(row[11]) if row[11] else {}
                    )
                    
                    self.devices[device.device_id] = device
                
                logger.info(f"디바이스 데이터 로드 완료: {len(self.devices)}개")
                
        except Exception as e:
            logger.error(f"디바이스 데이터 로드 실패: {e}")
    
    def register_store(self, store_data: Dict) -> Tuple[bool, str]:
        """매장 등록"""
        try:
            # 입력 데이터 검증
            validation_result = self._validate_store_data(store_data)
            if not validation_result[0]:
                return False, validation_result[1]
            
            # 매장 ID 생성
            store_id = self._generate_store_id(store_data['store_name'], store_data['city'])
            
            # 중복 확인
            if store_id in self.stores:
                return False, "이미 등록된 매장입니다."
            
            # 매장 객체 생성
            store = Store(
                store_id=store_id,
                store_name=store_data['store_name'],
                store_type=StoreType(store_data.get('store_type', 'franchise')),
                owner_id=store_data['owner_id'],
                address=store_data['address'],
                city=store_data['city'],
                state=store_data['state'],
                zip_code=store_data['zip_code'],
                country=store_data.get('country', 'KR'),
                phone=store_data['phone'],
                email=store_data['email'],
                status=StoreStatus.ACTIVE,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                last_activity=datetime.now().isoformat(),
                settings=store_data.get('settings', {})
            )
            
            # 데이터베이스에 저장
            self._save_store(store)
            
            # 메모리에 추가
            self.stores[store.store_id] = store
            
            logger.info(f"매장 등록 완료: {store.store_id} - {store.store_name}")
            return True, store_id
            
        except Exception as e:
            logger.error(f"매장 등록 실패: {e}")
            return False, str(e)
    
    def _validate_store_data(self, store_data: Dict) -> Tuple[bool, str]:
        """매장 데이터 검증"""
        try:
            required_fields = ['store_name', 'owner_id', 'address', 'city', 'state', 'zip_code', 'phone', 'email']
            
            for field in required_fields:
                if field not in store_data or not store_data[field]:
                    return False, f"필수 필드가 누락되었습니다: {field}"
            
            # 이메일 형식 검증
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, store_data['email']):
                return False, "올바른 이메일 형식이 아닙니다."
            
            # 전화번호 형식 검증
            phone_pattern = r'^[\d\-\+\(\)\s]+$'
            if not re.match(phone_pattern, store_data['phone']):
                return False, "올바른 전화번호 형식이 아닙니다."
            
            return True, "검증 통과"
            
        except Exception as e:
            logger.error(f"매장 데이터 검증 실패: {e}")
            return False, str(e)
    
    def _generate_store_id(self, store_name: str, city: str) -> str:
        """매장 ID 생성"""
        try:
            # 매장명과 도시명을 기반으로 ID 생성
            base_string = f"{store_name}_{city}".replace(" ", "_").lower()
            hash_object = hashlib.md5(base_string.encode())
            hash_hex = hash_object.hexdigest()[:8]
            return f"store_{hash_hex}"
            
        except Exception as e:
            logger.error(f"매장 ID 생성 실패: {e}")
            return f"store_{int(time.time())}"
    
    def update_store(self, store_id: str, updates: Dict) -> bool:
        """매장 정보 업데이트"""
        try:
            if store_id not in self.stores:
                return False
            
            store = self.stores[store_id]
            
            # 업데이트할 필드들
            for field, value in updates.items():
                if hasattr(store, field):
                    if field == 'store_type':
                        setattr(store, field, StoreType(value))
                    elif field == 'status':
                        setattr(store, field, StoreStatus(value))
                    else:
                        setattr(store, field, value)
            
            store.updated_at = datetime.now().isoformat()
            store.last_activity = datetime.now().isoformat()
            
            # 데이터베이스 업데이트
            self._save_store(store)
            
            logger.info(f"매장 정보 업데이트 완료: {store_id}")
            return True
            
        except Exception as e:
            logger.error(f"매장 정보 업데이트 실패: {e}")
            return False
    
    def delete_store(self, store_id: str) -> bool:
        """매장 삭제"""
        try:
            if store_id not in self.stores:
                return False
            
            # 관련 디바이스들도 삭제
            self._delete_store_devices(store_id)
            
            # 데이터베이스에서 삭제
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM stores WHERE store_id = ?', (store_id,))
                cursor.execute('DELETE FROM store_metrics WHERE store_id = ?', (store_id,))
                conn.commit()
            
            # 메모리에서 삭제
            del self.stores[store_id]
            
            logger.info(f"매장 삭제 완료: {store_id}")
            return True
            
        except Exception as e:
            logger.error(f"매장 삭제 실패: {e}")
            return False
    
    def get_store(self, store_id: str) -> Optional[Dict]:
        """매장 정보 조회"""
        try:
            if store_id not in self.stores:
                return None
            
            store = self.stores[store_id]
            store_dict = asdict(store)
            store_dict['store_type'] = store.store_type.value
            store_dict['status'] = store.status.value
            
            return store_dict
            
        except Exception as e:
            logger.error(f"매장 정보 조회 실패: {e}")
            return None
    
    def get_stores_by_owner(self, owner_id: str) -> List[Dict]:
        """소유자별 매장 목록 조회"""
        try:
            stores = []
            
            for store in self.stores.values():
                if store.owner_id == owner_id:
                    store_dict = asdict(store)
                    store_dict['store_type'] = store.store_type.value
                    store_dict['status'] = store.status.value
                    stores.append(store_dict)
            
            return stores
            
        except Exception as e:
            logger.error(f"소유자별 매장 목록 조회 실패: {e}")
            return []
    
    def get_all_stores(self, status: str = None) -> List[Dict]:
        """전체 매장 목록 조회"""
        try:
            stores = []
            
            for store in self.stores.values():
                if status is None or store.status.value == status:
                    store_dict = asdict(store)
                    store_dict['store_type'] = store.store_type.value
                    store_dict['status'] = store.status.value
                    stores.append(store_dict)
            
            return stores
            
        except Exception as e:
            logger.error(f"전체 매장 목록 조회 실패: {e}")
            return []
    
    def add_device(self, device_data: Dict) -> Tuple[bool, str]:
        """디바이스 추가"""
        try:
            # 매장 존재 확인
            if device_data['store_id'] not in self.stores:
                return False, "존재하지 않는 매장입니다."
            
            # 디바이스 ID 생성
            device_id = self._generate_device_id(device_data['device_type'], device_data['serial_number'])
            
            # 중복 확인
            if device_id in self.devices:
                return False, "이미 등록된 디바이스입니다."
            
            # 디바이스 객체 생성
            device = StoreDevice(
                device_id=device_id,
                store_id=device_data['store_id'],
                device_name=device_data['device_name'],
                device_type=device_data['device_type'],
                model=device_data['model'],
                serial_number=device_data['serial_number'],
                status=DeviceStatus.ONLINE,
                installed_at=datetime.now().isoformat(),
                last_maintenance=device_data.get('last_maintenance', ''),
                next_maintenance=device_data.get('next_maintenance', ''),
                warranty_expires=device_data.get('warranty_expires', ''),
                settings=device_data.get('settings', {})
            )
            
            # 데이터베이스에 저장
            self._save_device(device)
            
            # 메모리에 추가
            self.devices[device.device_id] = device
            
            # 매장 메트릭 업데이트
            self._update_store_metrics(device.store_id)
            
            logger.info(f"디바이스 추가 완료: {device.device_id} - {device.device_name}")
            return True, device_id
            
        except Exception as e:
            logger.error(f"디바이스 추가 실패: {e}")
            return False, str(e)
    
    def _generate_device_id(self, device_type: str, serial_number: str) -> str:
        """디바이스 ID 생성"""
        try:
            base_string = f"{device_type}_{serial_number}".replace(" ", "_").lower()
            hash_object = hashlib.md5(base_string.encode())
            hash_hex = hash_object.hexdigest()[:8]
            return f"device_{hash_hex}"
            
        except Exception as e:
            logger.error(f"디바이스 ID 생성 실패: {e}")
            return f"device_{int(time.time())}"
    
    def update_device(self, device_id: str, updates: Dict) -> bool:
        """디바이스 정보 업데이트"""
        try:
            if device_id not in self.devices:
                return False
            
            device = self.devices[device_id]
            
            # 업데이트할 필드들
            for field, value in updates.items():
                if hasattr(device, field):
                    if field == 'status':
                        setattr(device, field, DeviceStatus(value))
                    else:
                        setattr(device, field, value)
            
            # 데이터베이스 업데이트
            self._save_device(device)
            
            # 매장 메트릭 업데이트
            self._update_store_metrics(device.store_id)
            
            logger.info(f"디바이스 정보 업데이트 완료: {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"디바이스 정보 업데이트 실패: {e}")
            return False
    
    def delete_device(self, device_id: str) -> bool:
        """디바이스 삭제"""
        try:
            if device_id not in self.devices:
                return False
            
            device = self.devices[device_id]
            store_id = device.store_id
            
            # 데이터베이스에서 삭제
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM store_devices WHERE device_id = ?', (device_id,))
                conn.commit()
            
            # 메모리에서 삭제
            del self.devices[device_id]
            
            # 매장 메트릭 업데이트
            self._update_store_metrics(store_id)
            
            logger.info(f"디바이스 삭제 완료: {device_id}")
            return True
            
        except Exception as e:
            logger.error(f"디바이스 삭제 실패: {e}")
            return False
    
    def get_device(self, device_id: str) -> Optional[Dict]:
        """디바이스 정보 조회"""
        try:
            if device_id not in self.devices:
                return None
            
            device = self.devices[device_id]
            device_dict = asdict(device)
            device_dict['status'] = device.status.value
            
            return device_dict
            
        except Exception as e:
            logger.error(f"디바이스 정보 조회 실패: {e}")
            return None
    
    def get_devices_by_store(self, store_id: str) -> List[Dict]:
        """매장별 디바이스 목록 조회"""
        try:
            devices = []
            
            for device in self.devices.values():
                if device.store_id == store_id:
                    device_dict = asdict(device)
                    device_dict['status'] = device.status.value
                    devices.append(device_dict)
            
            return devices
            
        except Exception as e:
            logger.error(f"매장별 디바이스 목록 조회 실패: {e}")
            return []
    
    def get_store_metrics(self, store_id: str) -> Optional[Dict]:
        """매장 메트릭 조회"""
        try:
            if store_id not in self.stores:
                return None
            
            # 캐시된 메트릭이 있으면 반환
            if store_id in self.metrics_cache:
                cache_time = self.metrics_cache[store_id].get('last_updated', 0)
                if time.time() - cache_time < 300:  # 5분 캐시
                    return self.metrics_cache[store_id]
            
            # 메트릭 계산
            metrics = self._calculate_store_metrics(store_id)
            
            # 캐시에 저장
            self.metrics_cache[store_id] = metrics
            
            return metrics
            
        except Exception as e:
            logger.error(f"매장 메트릭 조회 실패: {e}")
            return None
    
    def _calculate_store_metrics(self, store_id: str) -> Dict:
        """매장 메트릭 계산"""
        try:
            # 매장의 디바이스들 조회
            store_devices = [device for device in self.devices.values() if device.store_id == store_id]
            
            total_devices = len(store_devices)
            online_devices = len([d for d in store_devices if d.status == DeviceStatus.ONLINE])
            offline_devices = len([d for d in store_devices if d.status == DeviceStatus.OFFLINE])
            maintenance_devices = len([d for d in store_devices if d.status == DeviceStatus.MAINTENANCE])
            error_devices = len([d for d in store_devices if d.status == DeviceStatus.ERROR])
            
            # 가동률 계산
            uptime_percentage = (online_devices / total_devices * 100) if total_devices > 0 else 0
            
            # 에너지 소비량 및 비용 (시뮬레이션)
            total_energy_consumption = online_devices * 50.0  # 디바이스당 50kW
            energy_cost = total_energy_consumption * 0.15  # kWh당 0.15원
            
            # 알림 수 (시뮬레이션)
            alert_count = error_devices * 2 + offline_devices
            
            metrics = {
                'store_id': store_id,
                'total_devices': total_devices,
                'online_devices': online_devices,
                'offline_devices': offline_devices,
                'maintenance_devices': maintenance_devices,
                'error_devices': error_devices,
                'total_energy_consumption': total_energy_consumption,
                'energy_cost': energy_cost,
                'uptime_percentage': uptime_percentage,
                'alert_count': alert_count,
                'last_updated': time.time()
            }
            
            # 데이터베이스에 저장
            self._save_store_metrics(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"매장 메트릭 계산 실패: {e}")
            return {}
    
    def _update_store_metrics(self, store_id: str):
        """매장 메트릭 업데이트"""
        try:
            # 캐시에서 제거하여 다음 조회 시 재계산
            if store_id in self.metrics_cache:
                del self.metrics_cache[store_id]
            
            # 메트릭 재계산
            self._calculate_store_metrics(store_id)
            
        except Exception as e:
            logger.error(f"매장 메트릭 업데이트 실패: {e}")
    
    def _save_store(self, store: Store):
        """매장 저장"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO stores 
                    (store_id, store_name, store_type, owner_id, address, city, state, zip_code, country, 
                     phone, email, status, created_at, updated_at, last_activity, settings)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    store.store_id,
                    store.store_name,
                    store.store_type.value,
                    store.owner_id,
                    store.address,
                    store.city,
                    store.state,
                    store.zip_code,
                    store.country,
                    store.phone,
                    store.email,
                    store.status.value,
                    store.created_at,
                    store.updated_at,
                    store.last_activity,
                    json.dumps(store.settings)
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"매장 저장 실패: {e}")
    
    def _save_device(self, device: StoreDevice):
        """디바이스 저장"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO store_devices 
                    (device_id, store_id, device_name, device_type, model, serial_number, status, 
                     installed_at, last_maintenance, next_maintenance, warranty_expires, settings)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    device.device_id,
                    device.store_id,
                    device.device_name,
                    device.device_type,
                    device.model,
                    device.serial_number,
                    device.status.value,
                    device.installed_at,
                    device.last_maintenance,
                    device.next_maintenance,
                    device.warranty_expires,
                    json.dumps(device.settings)
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"디바이스 저장 실패: {e}")
    
    def _save_store_metrics(self, metrics: Dict):
        """매장 메트릭 저장"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO store_metrics 
                    (store_id, total_devices, online_devices, offline_devices, maintenance_devices, 
                     error_devices, total_energy_consumption, energy_cost, uptime_percentage, 
                     alert_count, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metrics['store_id'],
                    metrics['total_devices'],
                    metrics['online_devices'],
                    metrics['offline_devices'],
                    metrics['maintenance_devices'],
                    metrics['error_devices'],
                    metrics['total_energy_consumption'],
                    metrics['energy_cost'],
                    metrics['uptime_percentage'],
                    metrics['alert_count'],
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"매장 메트릭 저장 실패: {e}")
    
    def _delete_store_devices(self, store_id: str):
        """매장의 모든 디바이스 삭제"""
        try:
            with connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM store_devices WHERE store_id = ?', (store_id,))
                conn.commit()
            
            # 메모리에서도 삭제
            devices_to_remove = [device_id for device_id, device in self.devices.items() 
                               if device.store_id == store_id]
            
            for device_id in devices_to_remove:
                del self.devices[device_id]
                
        except Exception as e:
            logger.error(f"매장 디바이스 삭제 실패: {e}")

# 전역 서비스 인스턴스
store_management_service = StoreManagementService()
