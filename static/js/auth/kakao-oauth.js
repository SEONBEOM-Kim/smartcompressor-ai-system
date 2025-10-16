// static/js/auth/kakao-oauth.js
class KakaoOAuth {
    async kakaoLogin() {
        try {
            // 카카오 로그인 URL 가져오기
            const response = await fetch('/api/kakao/login');
            
            // 502 오류 처리
            if (response.status === 502) {
                alert('서비스에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.');
                return;
            }
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                // 카카오 로그인 페이지로 리다이렉트
                window.location.href = data.login_url;
            } else {
                alert('카카오 로그인을 시작할 수 없습니다: ' + data.message);
            }
        } catch (error) {
            console.error('카카오 로그인 오류:', error);
            alert('카카오 로그인 중 오류가 발생했습니다. 페이지를 새로고침 후 다시 시도해주세요.');
        }
    }

    handleKakaoCallback() {
        const urlParams = new URLSearchParams(window.location.search);
        const kakaoLogin = urlParams.get('kakao_login');
        const sessionId = urlParams.get('session_id');
        
        if (kakaoLogin === 'success' && sessionId) {
            // 세션 ID를 localStorage에 저장
            localStorage.setItem('authToken', sessionId);
            
            // URL에서 파라미터 제거
            const newUrl = window.location.pathname;
            window.history.replaceState({}, document.title, newUrl);
            
            // 로그인 상태 업데이트
            updateLoginStatus();
            
            // 개선된 성공 화면 표시
            showLoginSuccessModal();
        }
    }
}