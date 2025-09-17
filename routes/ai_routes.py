#!/usr/bin/env python3
"""
AI 라우트
고성능 AI 진단 API 제공
"""

from flask import Blueprint, request, jsonify, current_app
import os
import time
import logging
from services.ai_service import ensemble_ai_service

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AI 라우트 블루프린트 생성
ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

@ai_bp.route('/status', methods=['GET'])
def get_ai_status():
    """AI 서비스 상태 조회"""
    try:
        status = ensemble_ai_service.get_ensemble_info()
        return jsonify({
            'success': True,
            'status': status,
            'message': 'AI 서비스 상태 조회 성공'
        })
    except Exception as e:
        logger.error(f"AI 상태 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'AI 서비스 상태 조회 실패'
        }), 500

@ai_bp.route('/analyze', methods=['POST'])
def analyze_audio():
    """AI 오디오 분석"""
    try:
        # 파일 업로드 확인
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': '오디오 파일이 없습니다',
                'message': '오디오 파일을 업로드해주세요'
            }), 400

        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({
                'success': False,
                'error': '파일명이 없습니다',
                'message': '유효한 오디오 파일을 선택해주세요'
            }), 400

        # 파일 저장
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)

        filename = f"ai_analysis_{int(time.time())}_{audio_file.filename}"
        file_path = os.path.join(upload_folder, filename)
        audio_file.save(file_path)

        # AI로 분석
        result = ensemble_ai_service.predict_ensemble(file_path)

        if result is None:
            return jsonify({
                'success': False,
                'error': 'AI 분석 실패',
                'message': '오디오 파일을 분석할 수 없습니다'
            }), 500

        # 파일 정리
        try:
            os.remove(file_path)
        except:
            pass

        return jsonify({
            'success': True,
            'result': result,
            'message': 'AI 분석 완료'
        })

    except Exception as e:
        logger.error(f"AI 분석 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'AI 분석 중 오류가 발생했습니다'
        }), 500

@ai_bp.route('/models', methods=['GET'])
def get_ai_models():
    """AI 모델 목록 조회"""
    try:
        models = []

        for model_name, model in ensemble_ai_service.ensemble_models.items():
            models.append({
                'name': model_name,
                'type': type(model).__name__,
                'status': 'loaded',
                'weight': ensemble_ai_service.ensemble_weights.get(model_name, 0),
                'description': f'AI 모델: {model_name}'
            })

        return jsonify({
            'success': True,
            'models': models,
            'message': 'AI 모델 목록 조회 성공'
        })

    except Exception as e:
        logger.error(f"AI 모델 목록 조회 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'AI 모델 목록 조회 실패'
        }), 500
