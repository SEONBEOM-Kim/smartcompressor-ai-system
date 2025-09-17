class PaymentService:
    @staticmethod
    def process_payment(plan_type, user_email):
        """결제 처리"""
        print(f'�� 결제 요청: {plan_type} 플랜, 사용자: {user_email}')
        
        # 결제 금액 계산
        amount = 9900 if plan_type == 'standard' else 19900
        
        return {
            'success': True,
            'message': '결제가 완료되었습니다!',
            'plan_type': plan_type,
            'amount': amount,
            'payment_url': f'http://signalcraft.kr/payment/success?plan={plan_type}'
        }
    
    @staticmethod
    def get_payment_amount(plan):
        """결제 금액 조회"""
        return '29,000원' if plan == 'standard' else '49,900원'
