// static/app.js (진입점만 유지)
const API_BASE_URL = window.location.origin;

// 전역 인스턴스
let authManager;
let navbarRenderer;
let modalManager;
let kakaoOAuth;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Signalcraft 애플리케이션이 초기화되었습니다.');
    
    // 인스턴스 생성
    authManager = new AuthManager();
    navbarRenderer = new NavbarRenderer();
    modalManager = new ModalManager();
    kakaoOAuth = new KakaoOAuth();
    
    // 초기화
    setupEventListeners();
    checkLoginSuccess();
    kakaoOAuth.handleKakaoCallback();
    authManager.updateLoginStatus();
});

// 이벤트 리스너 설정
function setupEventListeners() {
    console.log('이벤트 리스너를 설정합니다.');
}

// 전역 함수로 등록 (기존 호환성 유지)
window.showLoginModal = () => modalManager.showLoginModal();
window.showRegisterModal = () => modalManager.showRegisterModal();
window.updateLoginStatus = () => authManager.updateLoginStatus();
window.kakaoLogin = () => kakaoOAuth.kakaoLogin();
window.logout = () => authManager.logout();
window.checkLoginSuccess = checkLoginSuccess;
window.startDiagnosis = startDiagnosis;
window.goToDashboard = goToDashboard;
window.toggleMonitoring = toggleMonitoring;
window.stopMonitoring = stopMonitoring;
window.viewDiagnosisHistory = viewDiagnosisHistory;
window.saveMonitoringSettings = saveMonitoringSettings;
window.showLoggedInUI = (user) => navbarRenderer.showLoggedInUI(user);
window.showLoggedOutUI = () => navbarRenderer.showLoggedOutUI();

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