from flask import Blueprint, request, jsonify

payment_bp = Blueprint('payment', __name__, url_prefix='/payment')

# 결제 준비
@payment_bp.route('/ready', methods=['POST'])
def payment_ready():
    try:
        data = request.get_json()
        plan_type = data.get('plan_type', 'standard')
        user_email = data.get('user_email', 'test@example.com')

        print(f'💳 결제 요청: {plan_type} 플랜, 사용자: {user_email}')

        return jsonify({
            'success': True,
            'message': '결제가 완료되었습니다!',
            'plan_type': plan_type,
            'amount': 9900 if plan_type == 'standard' else 19900,
            'payment_url': f'http://signalcraft.kr/payment/success?plan={plan_type}'
        })
    except Exception as e:
        print(f"결제 오류: {e}")
        return jsonify({
            'success': False,
            'message': '결제 중 오류가 발생했습니다.'
        })

# 결제 성공 페이지
@payment_bp.route('/success')
def payment_success():
    plan = request.args.get('plan', 'standard')
    amount = '29,000원' if plan == 'standard' else '49,900원'

    return f'''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>결제 안내</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .payment-container {{ max-width: 600px; margin: 50px auto; padding: 40px; text-align: center; background: white; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
            .account-info {{ background: #f8f9fa; border-radius: 10px; padding: 20px; margin: 20px 0; border-left: 5px solid #6c5ce7; }}
        </style>
    </head>
    <body style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
        <div class="payment-container">
            <h2>💳 결제 안내</h2>
            <p>선택하신 {plan.title()} 플랜</p>
            <h3 style="color: #6c5ce7;">결제 금액: {amount}</h3>

            <div class="account-info">
                <h5>🏦 계좌이체 안내</h5>
                <p><strong>국민은행 101401-04-197042</strong></p>
                <p><strong>예금주: 김선범</strong></p>
            </div>

            <div class="alert alert-info">
                <strong>입금 확인 후 서비스가 활성화됩니다.</strong><br>
                입금 후 연락처로 문의해주세요.
            </div>

            <a href="/" class="btn btn-primary">메인으로 돌아가기</a>
        </div>
    </body>
    </html>
    '''

# 앙상블 AI 결제 플랜 조회
@payment_bp.route('/plans', methods=['GET'])
def get_payment_plans():
    """결제 플랜 조회 (앙상블 AI 포함)"""
    try:
        plans = [
            {
                'id': 'basic',
                'name': '기본 플랜',
                'price': 50000,
                'features': ['월 100회 분석', '기본 AI 모델', '이메일 지원'],
                'ai_models': ['lightweight']
            },
            {
                'id': 'premium',
                'name': '프리미엄 플랜',
                'price': 100000,
                'features': ['월 500회 분석', '앙상블 AI 모델', '실시간 모니터링', '전화 지원'],
                'ai_models': ['lightweight', 'ensemble']
            },
            {
                'id': 'enterprise',
                'name': '엔터프라이즈 플랜',
                'price': 200000,
                'features': ['무제한 분석', '고성능 AI 모델', '24시간 모니터링', '전담 지원'],
                'ai_models': ['lightweight', 'ensemble', 'mimii']
            }
        ]
        
        return jsonify({
            'success': True,
            'plans': plans
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'결제 플랜 조회 오류: {str(e)}'
        }), 500

# 앙상블 AI 결제 처리
@payment_bp.route('/process', methods=['POST'])
def process_payment():
    """결제 처리 (앙상블 AI 포함)"""
    try:
        data = request.get_json()
        plan_id = data.get('plan_id')
        amount = data.get('amount')
        user_email = data.get('user_email', 'test@example.com')
        
        if not plan_id or not amount:
            return jsonify({
                'success': False,
                'message': '결제 정보가 올바르지 않습니다.'
            }), 400
        
        # 플랜별 AI 모델 접근 권한 설정
        ai_access = {
            'basic': ['lightweight'],
            'premium': ['lightweight', 'ensemble'],
            'enterprise': ['lightweight', 'ensemble', 'mimii']
        }
        
        # 실제로는 토스페이먼츠 API 호출
        # 여기서는 시뮬레이션
        
        return jsonify({
            'success': True,
            'message': '결제가 완료되었습니다.',
            'payment_id': f'PAY_{int(time.time())}',
            'amount': amount,
            'plan_id': plan_id,
            'ai_access': ai_access.get(plan_id, ['lightweight']),
            'payment_url': f'http://signalcraft.kr/payment/success?plan={plan_id}'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'결제 처리 오류: {str(e)}'
        }), 500

# 앙상블 AI 서비스 활성화
@payment_bp.route('/activate', methods=['POST'])
def activate_service():
    """서비스 활성화 (앙상블 AI 포함)"""
    try:
        data = request.get_json()
        plan_id = data.get('plan_id')
        user_email = data.get('user_email')
        
        if not plan_id or not user_email:
            return jsonify({
                'success': False,
                'message': '활성화 정보가 올바르지 않습니다.'
            }), 400
        
        # 플랜별 서비스 활성화
        services = {
            'basic': {
                'ai_analysis': True,
                'ensemble_ai': False,
                'realtime_monitoring': False,
                'priority_support': False
            },
            'premium': {
                'ai_analysis': True,
                'ensemble_ai': True,
                'realtime_monitoring': True,
                'priority_support': True
            },
            'enterprise': {
                'ai_analysis': True,
                'ensemble_ai': True,
                'realtime_monitoring': True,
                'priority_support': True,
                'dedicated_support': True,
                'custom_models': True
            }
        }
        
        return jsonify({
            'success': True,
            'message': '서비스가 활성화되었습니다.',
            'plan_id': plan_id,
            'services': services.get(plan_id, services['basic']),
            'expires_at': '2024-12-31 23:59:59'  # 실제로는 계산된 만료일
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'서비스 활성화 오류: {str(e)}'
        }), 500
