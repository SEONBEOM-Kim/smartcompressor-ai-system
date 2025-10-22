#!/usr/bin/env python3
"""
AI 명령행 인터페이스
Node.js에서 Python AI 서비스를 호출하기 위한 CLI
"""

import sys
import json
import argparse
from services.ai_service import unified_ai_service
from services.field_data_collection import field_data_collector
from services.model_retraining import model_retraining_service

def analyze_audio(audio_path):
    """오디오 분석"""
    try:
        result = unified_ai_service.analyze_audio(audio_path)
        return {
            'success': True,
            'result': result
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def lightweight_analyze(audio_path):
    """경량 오디오 분석"""
    try:
        result = unified_ai_service.analyze_audio(audio_path, model_type='lightweight')
        return {
            'success': True,
            'result': result
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def collect_field_data(data):
    """현장 데이터 수집"""
    try:
        success = field_data_collector.collect_uncertain_predictions(
            store_id=data.get('store_id', ''),
            device_id=data.get('device_id', ''),
            audio_file_path=data.get('audio_file_path', ''),
            ai_prediction=data.get('ai_prediction', ''),
            ai_confidence=data.get('ai_confidence', 0.0),
            environmental_conditions=data.get('environmental_conditions', {})
        )
        
        return {
            'success': success,
            'data_id': 'pending' if success else None
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def get_retraining_status():
    """재훈련 상태 조회"""
    try:
        status = model_retraining_service.get_retraining_status()
        return {
            'success': True,
            'status': status
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def auto_retrain():
    """자동 재훈련 실행"""
    try:
        result = model_retraining_service.auto_retrain_if_needed()
        return {
            'success': True,
            'result': result
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def main():
    parser = argparse.ArgumentParser(description='AI 서비스 CLI')
    parser.add_argument('--analyze', help='오디오 파일 분석')
    parser.add_argument('--lightweight', help='경량 오디오 분석')
    parser.add_argument('--collect-data', action='store_true', help='현장 데이터 수집')
    parser.add_argument('--retraining-status', action='store_true', help='재훈련 상태 조회')
    parser.add_argument('--auto-retrain', action='store_true', help='자동 재훈련 실행')
    parser.add_argument('--version', action='store_true', help='버전 정보')
    
    args = parser.parse_args()
    
    if args.version:
        print(json.dumps({
            'success': True,
            'version': '1.0.0',
            'service': 'AI CLI'
        }))
        return
    
    if args.analyze:
        result = analyze_audio(args.analyze)
        print(json.dumps(result))
        return
    
    if args.lightweight:
        result = lightweight_analyze(args.lightweight)
        print(json.dumps(result))
        return
    
    if args.collect_data:
        # 표준 입력에서 데이터 읽기
        try:
            data = json.loads(sys.stdin.read())
            result = collect_field_data(data)
            print(json.dumps(result))
        except Exception as e:
            print(json.dumps({
                'success': False,
                'error': f'데이터 파싱 오류: {str(e)}'
            }))
        return
    
    if args.retraining_status:
        result = get_retraining_status()
        print(json.dumps(result))
        return
    
    if args.auto_retrain:
        result = auto_retrain()
        print(json.dumps(result))
        return
    
    # 기본 응답
    print(json.dumps({
        'success': False,
        'error': '유효하지 않은 명령입니다.'
    }))

if __name__ == '__main__':
    main()
