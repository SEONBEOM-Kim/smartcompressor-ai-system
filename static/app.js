// static/app.js (진입점만 유지)
const API_BASE_URL = window.location.origin;

// 전역 인스턴스
let authManager;
let navbarRenderer;
let modalManager;
let kakaoOAuth;

// Initialize managers after DOM is loaded
function initApp() {
    console.log('Signalcraft 애플리케이션이 초기화되었습니다.');
    
    // 인스턴스 생성 - with checks to ensure classes exist
    if (typeof AuthManager !== 'undefined') {
        authManager = new AuthManager();
    } else {
        console.error('AuthManager class is not available');
    }
    
    if (typeof NavbarRenderer !== 'undefined') {
        navbarRenderer = new NavbarRenderer();
    } else {
        console.error('NavbarRenderer class is not available');
    }
    
    if (typeof ModalManager !== 'undefined') {
        modalManager = new ModalManager();
    } else {
        console.error('ModalManager class is not available');
    }
    
    if (typeof KakaoOAuth !== 'undefined') {
        kakaoOAuth = new KakaoOAuth();
    } else {
        console.error('KakaoOAuth class is not available');
    }
    
    // 초기화
    setupEventListeners();
    checkLoginSuccess();
    if (kakaoOAuth) {
        kakaoOAuth.handleKakaoCallback();
    }
    if (authManager) {
        authManager.updateLoginStatus();
    }
    
    // Dispatch a custom event to signal that initialization is complete
    window.dispatchEvent(new CustomEvent('managersInitialized'));
}

// Ensure initialization happens after DOM is fully loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    // DOM is already loaded, run init immediately
    initApp();
}

// 이벤트 리스너 설정
function setupEventListeners() {
    console.log('이벤트 리스너를 설정합니다.');
}

// 전역 함수로 등록 (기존 호환성 유지)
window.showLoginModal = () => {
    if (typeof ModalManager !== 'undefined' && modalManager) {
        modalManager.showLoginModal();
    } else {
        // If managers aren't initialized, wait a bit and try again
        setTimeout(() => {
            if (modalManager) {
                modalManager.showLoginModal();
            } else {
                console.error('ModalManager is still not available after timeout');
            }
        }, 100);
    }
};
window.showRegisterModal = () => {
    if (typeof ModalManager !== 'undefined' && modalManager) {
        modalManager.showRegisterModal();
    } else {
        // If managers aren't initialized, wait a bit and try again
        setTimeout(() => {
            if (modalManager) {
                modalManager.showRegisterModal();
            } else {
                console.error('ModalManager is still not available after timeout');
            }
        }, 100);
    }
};
window.showPasswordResetModal = () => {
    if (typeof ModalManager !== 'undefined' && modalManager) {
        modalManager.showPasswordResetModal();
    } else {
        // If managers aren't initialized, wait a bit and try again
        setTimeout(() => {
            if (modalManager) {
                modalManager.showPasswordResetModal();
            } else {
                console.error('ModalManager is still not available after timeout');
            }
        }, 100);
    }
};
window.updateLoginStatus = () => {
    if (typeof AuthManager !== 'undefined' && authManager) {
        authManager.updateLoginStatus();
    } else {
        console.error('AuthManager not initialized yet.');
    }
};
window.kakaoLogin = () => {
    if (typeof KakaoOAuth !== 'undefined' && kakaoOAuth) {
        kakaoOAuth.kakaoLogin();
    } else {
        console.error('KakaoOAuth not initialized yet.');
    }
};
window.googleLogin = () => {
    // Google OAuth 로그인 구현
    alert('구글 로그인 기능은 현재 개발 중입니다. 이메일 로그인을 이용해주세요.');
    // 실제 구현에서는 구글 OAuth 인증 창을 여는 로직이 들어갑니다
};
window.logout = () => {
    if (typeof AuthManager !== 'undefined' && authManager) {
        authManager.logout();
    } else {
        console.error('AuthManager not initialized yet.');
    }
};
window.checkLoginSuccess = checkLoginSuccess;
window.startDiagnosis = startDiagnosis;
window.goToDashboard = goToDashboard;
window.toggleMonitoring = toggleMonitoring;
window.stopMonitoring = stopMonitoring;
window.viewDiagnosisHistory = viewDiagnosisHistory;
window.saveMonitoringSettings = saveMonitoringSettings;
window.showLoggedInUI = (user) => {
    if (typeof NavbarRenderer !== 'undefined' && navbarRenderer) {
        navbarRenderer.showLoggedInUI(user);
    } else {
        console.error('NavbarRenderer not initialized yet.');
    }
};
window.showLoggedOutUI = () => {
    if (typeof NavbarRenderer !== 'undefined' && navbarRenderer) {
        navbarRenderer.showLoggedOutUI();
    } else {
        console.error('NavbarRenderer not initialized yet.');
    }
};

// 진단 시작하기 함수
function startDiagnosis() {
    console.log('진단 시작하기');
    // 진단 섹션으로 스크롤하거나 진단 모달 표시
    const diagnosisSection = document.getElementById('diagnosis');
    if (diagnosisSection) {
        diagnosisSection.scrollIntoView({ behavior: 'smooth' });
    } else {
        alert('진단 기능을 준비 중입니다.');
    }
}

// 대시보드로 이동 함수
function goToDashboard() {
    console.log('대시보드로 이동');
    const dashboardSection = document.getElementById('dashboard');
    if (dashboardSection) {
        dashboardSection.scrollIntoView({ behavior: 'smooth' });
    } else {
        alert('대시보드 기능을 준비 중입니다.');
    }
}

// 모니터링 토글 함수
function toggleMonitoring() {
    console.log('모니터링 토글');
    const btn = event.target;
    if (btn.innerHTML.includes('시작')) {
        btn.innerHTML = '<i class="fas fa-stop me-2"></i>모니터링 중지';
        btn.className = 'btn btn-danger';
        // 실제 모니터링 시작 로직
        alert('모니터링이 시작되었습니다.');
    } else {
        btn.innerHTML = '<i class="fas fa-play me-2"></i>모니터링 시작';
        btn.className = 'btn btn-info';
        // 실제 모니터링 중지 로직
        alert('모니터링이 중지되었습니다.');
    }
}

// 모니터링 중지 함수
function stopMonitoring() {
    console.log('모니터링 중지');
    alert('모니터링이 중지되었습니다.');
}

// 진단 기록 보기 함수
function viewDiagnosisHistory() {
    console.log('진단 기록 보기');
    const diagnosisSection = document.getElementById('diagnosis');
    if (diagnosisSection) {
        diagnosisSection.scrollIntoView({ behavior: 'smooth' });
    }
}

// 모니터링 설정 저장 함수
function saveMonitoringSettings() {
    console.log('모니터링 설정 저장');
    alert('설정이 저장되었습니다.');
}