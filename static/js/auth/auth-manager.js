// static/js/auth/auth-manager.js
class AuthManager {
    constructor() {
        this.currentUser = null;
        this.authToken = null;
    }

    async updateLoginStatus() {
        const token = localStorage.getItem('authToken');
        if (!token) {
            showLoggedOutUI();
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/auth/verify`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            const data = await response.json();
            
            if (data.success && data.user) {
                showLoggedInUI(data.user);
            } else {
                showLoggedOutUI();
            }
        } catch (error) {
            console.error('로그인 상태 확인 오류:', error);
            showLoggedOutUI();
        }
    }

    async handleLogin(event) {
        event.preventDefault();
        
        const username = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;
        
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (data.success) {
                this.currentUser = data.user;
                
                // 로컬 스토리지에 저장
                localStorage.setItem('currentUser', JSON.stringify(data.user));
                localStorage.setItem('authToken', 'session-token'); // 임시 토큰
                
                // UI 직접 업데이트 (세션 검증 없이)
                showLoggedInUI(data.user);
                
                // 모달 닫기 (Bootstrap 5 방식)
                const modal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
                if (modal) {
                    modal.hide();
                }
                
                // 역할에 따른 리다이렉트
                if (data.user.role === 'admin') {
                    alert('로그인 성공! 관리자 대시보드로 이동합니다.');
                    window.location.href = '/admin/';
                } else {
                    alert('로그인 성공! 환영합니다.');
                    // 일반 사용자는 메인 페이지에 머물거나 사용자 대시보드로 이동
                    // window.location.href = '/dashboard'; // 사용자 대시보드가 있다면
                    // 현재는 메인 페이지에 머물도록 함
                }
            } else {
                alert('로그인 실패: ' + data.message);
            }
        } catch (error) {
            console.error('로그인 오류:', error);
            alert('로그인 중 오류가 발생했습니다.');
        }
    }

    async logout() {
        const token = localStorage.getItem('authToken');
        
        try {
            const response = await fetch(`${API_BASE_URL}/api/auth/logout`, { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ sessionId: token })
            });
            
            const data = await response.json();
            
            if (data.success) {
                localStorage.removeItem('authToken');
                showLoggedOutUI();
                console.log('로그아웃 성공');
            }
        } catch (error) {
            console.error('로그아웃 오류:', error);
            localStorage.removeItem('authToken');
            showLoggedOutUI();
        }
    }
}

// URL 파라미터 처리
function checkLoginSuccess() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('login') === 'success') {
        console.log('로그인 성공 감지');
        updateLoginStatus();
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}