@customer_bp.route('/dashboard')
def customer_dashboard():
    # 로그인 체크
    if not session.get('user_id'):
        return redirect('/login')
    
    return render_template('customer/dashboard.html')
