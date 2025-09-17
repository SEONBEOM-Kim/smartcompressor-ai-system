// Signalcraft 웹 애플리케이션 JavaScript

// API 기본 URL
const API_BASE_URL = 'http://3.39.124.0:8000';

// 전역 변수
let currentUser = null;
let authToken = null;

// DOM 로드 완료 시 실행
document.addEventListener('DOMContentLoaded', function() {
    console.log('Signalcraft 애플리케이션이 초기화되었습니다.');
    setupEventListeners();
    checkLoginSuccess();
    updateLoginStatus();
});

// URL 파라미터 처리
function checkLoginSuccess() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('login') === 'success') {
        console.log('로그인 성공 감지');
        updateLoginStatus();
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}

// 로그인 상태 관리
function updateLoginStatus() {
    fetch('/auth/status')
        .then(response => response.json())
        .then(data => {
            if (data.authenticated && data.user) {
                showLoggedInUI(data.user);
            } else {
                showLoggedOutUI();
            }
        })
        .catch(error => {
            console.error('로그인 상태 확인 오류:', error);
            showLoggedOutUI();
        });
}

// 로그인된 UI 표시 (수정된 버전)
function showLoggedInUI(user) {
    console.log('로그인된 UI 표시:', user);
    
    const userName = user.name || user.username || user.email || '사용자';
    
    // 기존 userInfo 제거
    const existingUserInfo = document.getElementById('userInfo');
    if (existingUserInfo) {
        existingUserInfo.remove();
    }
    
    // 로그인 버튼들 숨기기
    const loginBtn = document.querySelector('button[onclick="showLoginModal()"]');
    const registerBtn = document.querySelector('button[onclick="showRegisterModal()"]');
    const kakaoBtn = document.querySelector('a[href="/auth/kakao"]');
    
    if (loginBtn) loginBtn.style.display = 'none';
    if (registerBtn) registerBtn.style.display = 'none';
    if (kakaoBtn) kakaoBtn.style.display = 'none';
    
    // 사용자 정보 추가
    const navbar = document.querySelector('.navbar-nav');
    if (navbar) {
        const userInfo = document.createElement('li');
        userInfo.className = 'nav-item';
        userInfo.innerHTML = `
            <span class="nav-link">안녕하세요, ${userName}님!</span>
            <button class="btn btn-outline-light ms-2" onclick="logout()">로그아웃</button>
        `;
        navbar.appendChild(userInfo);
    }
}

// 로그아웃된 UI 표시
function showLoggedOutUI() {
    console.log('로그아웃된 UI 표시');
    
    // userInfo 제거
    const userInfo = document.getElementById('userInfo');
    if (userInfo) {
        userInfo.remove();
    }
    
    // 로그인/회원가입/카카오 로그인 버튼 다시 표시
    const loginBtn = document.querySelector('button[onclick="showLoginModal()"]');
    const registerBtn = document.querySelector('button[onclick="showRegisterModal()"]');
    const kakaoBtn = document.querySelector('a[href="/auth/kakao"]');
    
    if (loginBtn) loginBtn.style.display = 'inline-block';
    if (registerBtn) registerBtn.style.display = 'inline-block';
    if (kakaoBtn) kakaoBtn.style.display = 'inline-block';
}

// 로그아웃
function logout() {
    fetch('/auth/logout', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showLoggedOutUI();
                console.log('로그아웃 성공');
            }
        })
        .catch(error => {
            console.error('로그아웃 오류:', error);
        });
}

// 로그인 모달 표시
function showLoginModal() {
    console.log('로그인 모달을 표시합니다.');
    // 모달 로직은 나중에 구현
}

// 회원가입 모달 표시
function showRegisterModal() {
    console.log('회원가입 모달을 표시합니다.');
    // 모달 로직은 나중에 구현
}

// 이벤트 리스너 설정
function setupEventListeners() {
    console.log('이벤트 리스너를 설정합니다.');
}

// 전역 함수로 등록
window.showLoginModal = showLoginModal;
window.showRegisterModal = showRegisterModal;
window.updateLoginStatus = updateLoginStatus;
window.showLoggedInUI = showLoggedInUI;
window.showLoggedOutUI = showLoggedOutUI;
window.logout = logout;
window.checkLoginSuccess = checkLoginSuccess;
