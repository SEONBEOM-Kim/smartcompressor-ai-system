from flask import Blueprint, request, jsonify
import os
import time
import logging
from datetime import datetime
import json

audio_bp = Blueprint('audio', __name__, url_prefix='/api/audio')

@audio_bp.route('/upload', methods=['POST'])
def upload_audio():
    try:
        # 헤더에서 메타데이터 추출
        device_id = request.headers.get('X-Device-ID', 'unknown')
        sample_rate = request.headers.get('X-Sample-Rate', '16000')
        bits_per_sample = request.headers.get('X-Bits-Per-Sample', '16')
        
        # 오디오 데이터 받기
        audio_data = request.data
        
        if not audio_data:
            return jsonify({'error': '오디오 데이터가 없습니다.'}), 400
        
        # 파일명 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"esp32_audio_{device_id}_{timestamp}.raw"
        
        # 업로드 디렉토리 생성
        upload_dir = 'uploads/esp32_audio'
        os.makedirs(upload_dir, exist_ok=True)
        
        # 파일 저장
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(audio_data)
        
        # 메타데이터 저장
        metadata = {
            'device_id': device_id,
            'sample_rate': int(sample_rate),
            'bits_per_sample': int(bits_per_sample),
            'file_size': len(audio_data),
            'timestamp': timestamp,
            'file_path': file_path
        }
        
        # 로그 저장
        logging.info(f"ESP-32 오디오 업로드: {metadata}")
        
        return jsonify({
            'status': 'success',
            'message': '오디오 업로드 완료',
            'filename': filename,
            'metadata': metadata
        })
        
    except Exception as e:
        logging.error(f"오디오 업로드 오류: {e}")
        return jsonify({'error': str(e)}), 500

@audio_bp.route('/status', methods=['GET'])
def get_audio_status():
    return jsonify({
        'status': 'active',
        'message': 'ESP-32 오디오 서비스 정상 작동',
        'timestamp': datetime.now().isoformat()
    })
