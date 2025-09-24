"""
암호화 서비스 - Stripe & AWS 보안 시스템 벤치마킹
전송 중 및 저장 시 데이터 암호화, 키 관리 시스템
"""

import os
import base64
import hashlib
import secrets
import logging
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import json

logger = logging.getLogger(__name__)

class EncryptionType(Enum):
    """암호화 타입"""
    AES_256_GCM = "aes_256_gcm"
    AES_256_CBC = "aes_256_cbc"
    RSA_2048 = "rsa_2048"
    RSA_4096 = "rsa_4096"
    FERNET = "fernet"

class KeyType(Enum):
    """키 타입"""
    MASTER = "master"
    DATA = "data"
    COMMUNICATION = "communication"
    BACKUP = "backup"

@dataclass
class EncryptionKey:
    """암호화 키 정보"""
    key_id: str
    key_type: KeyType
    encryption_type: EncryptionType
    key_data: bytes
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    version: int = 1

@dataclass
class EncryptedData:
    """암호화된 데이터"""
    data: bytes
    key_id: str
    encryption_type: EncryptionType
    iv: Optional[bytes] = None
    tag: Optional[bytes] = None
    metadata: Dict = None

class EncryptionService:
    """
    Stripe & AWS 보안 시스템을 벤치마킹한 고급 암호화 서비스
    """
    
    def __init__(self):
        self.keys: Dict[str, EncryptionKey] = {}
        self.master_password = self._get_or_create_master_password()
        self.key_rotation_interval = timedelta(days=90)
        
        self._initialize_default_keys()
        logger.info("EncryptionService 초기화 완료")

    def _get_or_create_master_password(self) -> str:
        """마스터 비밀번호 생성 또는 조회"""
        password = os.getenv('MASTER_ENCRYPTION_PASSWORD')
        if not password:
            password = secrets.token_urlsafe(32)
            logger.warning("MASTER_ENCRYPTION_PASSWORD 환경변수가 설정되지 않았습니다. 임시 키를 생성합니다.")
        return password

    def _initialize_default_keys(self):
        """기본 키 초기화"""
        # 마스터 키 생성
        master_key = self._generate_aes_key()
        self.keys["master_key"] = EncryptionKey(
            key_id="master_key",
            key_type=KeyType.MASTER,
            encryption_type=EncryptionType.AES_256_GCM,
            key_data=master_key,
            created_at=datetime.now()
        )
        
        # 데이터 암호화 키 생성
        data_key = self._generate_aes_key()
        self.keys["data_key"] = EncryptionKey(
            key_id="data_key",
            key_type=KeyType.DATA,
            encryption_type=EncryptionType.AES_256_GCM,
            key_data=data_key,
            created_at=datetime.now()
        )
        
        # 통신 암호화 키 생성
        comm_key = self._generate_aes_key()
        self.keys["comm_key"] = EncryptionKey(
            key_id="comm_key",
            key_type=KeyType.COMMUNICATION,
            encryption_type=EncryptionType.AES_256_GCM,
            key_data=comm_key,
            created_at=datetime.now()
        )

    def _generate_aes_key(self) -> bytes:
        """AES 키 생성"""
        return Fernet.generate_key()

    def _generate_rsa_keypair(self, key_size: int = 2048) -> Tuple[bytes, bytes]:
        """RSA 키 쌍 생성"""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        
        public_key = private_key.public_key()
        
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem, public_pem

    def _derive_key_from_password(self, password: str, salt: bytes) -> bytes:
        """비밀번호에서 키 유도"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password.encode())

    def encrypt_data(self, data: bytes, key_id: str = "data_key", 
                    encryption_type: EncryptionType = EncryptionType.AES_256_GCM) -> EncryptedData:
        """데이터 암호화"""
        if key_id not in self.keys:
            raise ValueError(f"키 {key_id}를 찾을 수 없습니다.")
        
        key = self.keys[key_id]
        if not key.is_active:
            raise ValueError(f"키 {key_id}가 비활성화되었습니다.")
        
        if encryption_type == EncryptionType.AES_256_GCM:
            return self._encrypt_aes_gcm(data, key)
        elif encryption_type == EncryptionType.AES_256_CBC:
            return self._encrypt_aes_cbc(data, key)
        elif encryption_type == EncryptionType.FERNET:
            return self._encrypt_fernet(data, key)
        else:
            raise ValueError(f"지원하지 않는 암호화 타입: {encryption_type}")

    def _encrypt_aes_gcm(self, data: bytes, key: EncryptionKey) -> EncryptedData:
        """AES-GCM 암호화"""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        
        aesgcm = AESGCM(key.key_data)
        iv = os.urandom(12)  # 96-bit IV for GCM
        encrypted_data = aesgcm.encrypt(iv, data, None)
        
        return EncryptedData(
            data=encrypted_data,
            key_id=key.key_id,
            encryption_type=EncryptionType.AES_256_GCM,
            iv=iv,
            metadata={"algorithm": "AES-GCM"}
        )

    def _encrypt_aes_cbc(self, data: bytes, key: EncryptionKey) -> EncryptedData:
        """AES-CBC 암호화"""
        iv = os.urandom(16)  # 128-bit IV for CBC
        cipher = Cipher(
            algorithms.AES(key.key_data),
            modes.CBC(iv),
            backend=default_backend()
        )
        
        encryptor = cipher.encryptor()
        
        # PKCS7 패딩
        padding_length = 16 - (len(data) % 16)
        padded_data = data + bytes([padding_length] * padding_length)
        
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        
        return EncryptedData(
            data=encrypted_data,
            key_id=key.key_id,
            encryption_type=EncryptionType.AES_256_CBC,
            iv=iv,
            metadata={"algorithm": "AES-CBC"}
        )

    def _encrypt_fernet(self, data: bytes, key: EncryptionKey) -> EncryptedData:
        """Fernet 암호화"""
        fernet = Fernet(key.key_data)
        encrypted_data = fernet.encrypt(data)
        
        return EncryptedData(
            data=encrypted_data,
            key_id=key.key_id,
            encryption_type=EncryptionType.FERNET,
            metadata={"algorithm": "Fernet"}
        )

    def decrypt_data(self, encrypted_data: EncryptedData) -> bytes:
        """데이터 복호화"""
        if encrypted_data.key_id not in self.keys:
            raise ValueError(f"키 {encrypted_data.key_id}를 찾을 수 없습니다.")
        
        key = self.keys[encrypted_data.key_id]
        if not key.is_active:
            raise ValueError(f"키 {encrypted_data.key_id}가 비활성화되었습니다.")
        
        if encrypted_data.encryption_type == EncryptionType.AES_256_GCM:
            return self._decrypt_aes_gcm(encrypted_data, key)
        elif encrypted_data.encryption_type == EncryptionType.AES_256_CBC:
            return self._decrypt_aes_cbc(encrypted_data, key)
        elif encrypted_data.encryption_type == EncryptionType.FERNET:
            return self._decrypt_fernet(encrypted_data, key)
        else:
            raise ValueError(f"지원하지 않는 암호화 타입: {encrypted_data.encryption_type}")

    def _decrypt_aes_gcm(self, encrypted_data: EncryptedData, key: EncryptionKey) -> bytes:
        """AES-GCM 복호화"""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        
        aesgcm = AESGCM(key.key_data)
        decrypted_data = aesgcm.decrypt(encrypted_data.iv, encrypted_data.data, None)
        
        return decrypted_data

    def _decrypt_aes_cbc(self, encrypted_data: EncryptedData, key: EncryptionKey) -> bytes:
        """AES-CBC 복호화"""
        cipher = Cipher(
            algorithms.AES(key.key_data),
            modes.CBC(encrypted_data.iv),
            backend=default_backend()
        )
        
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data.data) + decryptor.finalize()
        
        # PKCS7 패딩 제거
        padding_length = decrypted_data[-1]
        return decrypted_data[:-padding_length]

    def _decrypt_fernet(self, encrypted_data: EncryptedData, key: EncryptionKey) -> bytes:
        """Fernet 복호화"""
        fernet = Fernet(key.key_data)
        decrypted_data = fernet.decrypt(encrypted_data.data)
        
        return decrypted_data

    def encrypt_string(self, text: str, key_id: str = "data_key") -> str:
        """문자열 암호화"""
        data = text.encode('utf-8')
        encrypted = self.encrypt_data(data, key_id)
        
        # JSON으로 직렬화하여 반환
        encrypted_dict = {
            "data": base64.b64encode(encrypted.data).decode(),
            "key_id": encrypted.key_id,
            "encryption_type": encrypted.encryption_type.value,
            "iv": base64.b64encode(encrypted.iv).decode() if encrypted.iv else None,
            "metadata": encrypted.metadata
        }
        
        return json.dumps(encrypted_dict)

    def decrypt_string(self, encrypted_text: str) -> str:
        """문자열 복호화"""
        encrypted_dict = json.loads(encrypted_text)
        
        encrypted_data = EncryptedData(
            data=base64.b64decode(encrypted_dict["data"]),
            key_id=encrypted_dict["key_id"],
            encryption_type=EncryptionType(encrypted_dict["encryption_type"]),
            iv=base64.b64decode(encrypted_dict["iv"]) if encrypted_dict["iv"] else None,
            metadata=encrypted_dict.get("metadata", {})
        )
        
        decrypted_data = self.decrypt_data(encrypted_data)
        return decrypted_data.decode('utf-8')

    def encrypt_file(self, file_path: str, output_path: str, key_id: str = "data_key") -> bool:
        """파일 암호화"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            encrypted = self.encrypt_data(data, key_id)
            
            with open(output_path, 'wb') as f:
                f.write(encrypted.data)
                f.write(b'\n---ENCRYPTION_METADATA---\n')
                f.write(json.dumps({
                    "key_id": encrypted.key_id,
                    "encryption_type": encrypted.encryption_type.value,
                    "iv": base64.b64encode(encrypted.iv).decode() if encrypted.iv else None,
                    "metadata": encrypted.metadata
                }).encode())
            
            logger.info(f"파일 {file_path} 암호화 완료: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"파일 암호화 실패: {e}")
            return False

    def decrypt_file(self, encrypted_file_path: str, output_path: str) -> bool:
        """파일 복호화"""
        try:
            with open(encrypted_file_path, 'rb') as f:
                content = f.read()
            
            # 메타데이터 분리
            parts = content.split(b'\n---ENCRYPTION_METADATA---\n')
            if len(parts) != 2:
                raise ValueError("잘못된 암호화 파일 형식")
            
            encrypted_data_bytes = parts[0]
            metadata_json = parts[1].decode()
            metadata = json.loads(metadata_json)
            
            encrypted_data = EncryptedData(
                data=encrypted_data_bytes,
                key_id=metadata["key_id"],
                encryption_type=EncryptionType(metadata["encryption_type"]),
                iv=base64.b64decode(metadata["iv"]) if metadata["iv"] else None,
                metadata=metadata.get("metadata", {})
            )
            
            decrypted_data = self.decrypt_data(encrypted_data)
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            logger.info(f"파일 {encrypted_file_path} 복호화 완료: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"파일 복호화 실패: {e}")
            return False

    def generate_new_key(self, key_type: KeyType, encryption_type: EncryptionType = EncryptionType.AES_256_GCM) -> str:
        """새 키 생성"""
        key_id = f"{key_type.value}_{secrets.token_hex(8)}"
        
        if encryption_type in [EncryptionType.AES_256_GCM, EncryptionType.AES_256_CBC, EncryptionType.FERNET]:
            key_data = self._generate_aes_key()
        else:
            raise ValueError(f"지원하지 않는 암호화 타입: {encryption_type}")
        
        key = EncryptionKey(
            key_id=key_id,
            key_type=key_type,
            encryption_type=encryption_type,
            key_data=key_data,
            created_at=datetime.now(),
            expires_at=datetime.now() + self.key_rotation_interval
        )
        
        self.keys[key_id] = key
        logger.info(f"새 키 생성 완료: {key_id}")
        return key_id

    def rotate_key(self, old_key_id: str) -> str:
        """키 로테이션"""
        if old_key_id not in self.keys:
            raise ValueError(f"키 {old_key_id}를 찾을 수 없습니다.")
        
        old_key = self.keys[old_key_id]
        new_key_id = self.generate_new_key(old_key.key_type, old_key.encryption_type)
        
        # 기존 키 비활성화
        old_key.is_active = False
        
        logger.info(f"키 로테이션 완료: {old_key_id} -> {new_key_id}")
        return new_key_id

    def get_key_info(self, key_id: str) -> Optional[Dict]:
        """키 정보 조회"""
        if key_id not in self.keys:
            return None
        
        key = self.keys[key_id]
        return {
            "key_id": key.key_id,
            "key_type": key.key_type.value,
            "encryption_type": key.encryption_type.value,
            "created_at": key.created_at.isoformat(),
            "expires_at": key.expires_at.isoformat() if key.expires_at else None,
            "is_active": key.is_active,
            "version": key.version
        }

    def list_keys(self) -> List[Dict]:
        """키 목록 조회"""
        return [self.get_key_info(key_id) for key_id in self.keys.keys()]

    def deactivate_key(self, key_id: str) -> bool:
        """키 비활성화"""
        if key_id not in self.keys:
            return False
        
        self.keys[key_id].is_active = False
        logger.info(f"키 {key_id} 비활성화 완료")
        return True

    def delete_key(self, key_id: str) -> bool:
        """키 삭제"""
        if key_id not in self.keys:
            return False
        
        if self.keys[key_id].is_active:
            logger.warning(f"활성 키 {key_id}는 삭제할 수 없습니다. 먼저 비활성화하세요.")
            return False
        
        del self.keys[key_id]
        logger.info(f"키 {key_id} 삭제 완료")
        return True

    def hash_sensitive_data(self, data: str, salt: Optional[str] = None) -> str:
        """민감한 데이터 해시화 (일방향)"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        salted_data = f"{data}{salt}".encode('utf-8')
        hash_obj = hashlib.sha256(salted_data)
        return f"{hash_obj.hexdigest()}:{salt}"

    def verify_hashed_data(self, data: str, hashed_data: str) -> bool:
        """해시된 데이터 검증"""
        try:
            hash_value, salt = hashed_data.split(':')
            salted_data = f"{data}{salt}".encode('utf-8')
            hash_obj = hashlib.sha256(salted_data)
            return hash_obj.hexdigest() == hash_value
        except:
            return False

# 싱글톤 인스턴스
encryption_service = EncryptionService()
