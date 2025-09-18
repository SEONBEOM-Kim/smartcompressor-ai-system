// Signalcraft 웹 애플리케이션 JavaScript

// API 기본 URL - 통합 서버
const API_BASE_URL = window.location.origin;

// 전역 변수
let currentUser = null;
let authToken = null;

// DOM 로드 완료 시 실행
document.addEventListener('DOMContentLoaded', function() {
    console.log('Signalcraft 애플리케이션이 초기화되었습니다.');
    setupEventListeners();
    checkLoginSuccess();
    handleKakaoCallback(); // 카카오 로그인 콜백 처리
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
    const token = localStorage.getItem('authToken');
    if (!token) {
        showLoggedOutUI();
        return;
    }
    
    fetch(`${API_BASE_URL}/api/auth/verify`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
        .then(response => response.json())
        .then(data => {
        if (data.success && data.user) {
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

// 로그인된 UI 표시 (개선된 버전)
function showLoggedInUI(user) {
    console.log('로그인된 UI 표시:', user);
    
    const userName = user.name || user.username || user.email || '사용자';
    const userProfileImage = user.profile_image || user.thumbnail_image || null;
    
    // 기존 userInfo 제거
    const existingUserInfo = document.getElementById('userInfo');
    if (existingUserInfo) {
        existingUserInfo.remove();
    }
    
    // 로그인 버튼들 숨기기
    const loginBtn = document.querySelector('button[onclick="showLoginModal()"]');
    const registerBtn = document.querySelector('button[onclick="showRegisterModal()"]');
    const kakaoBtn = document.querySelector('button[onclick="kakaoLogin()"]');
    
    if (loginBtn) loginBtn.style.display = 'none';
    if (registerBtn) registerBtn.style.display = 'none';
    if (kakaoBtn) kakaoBtn.style.display = 'none';
    
    // 데모 섹션 숨기기 (로그인 후에는 체험 모듈 숨김)
    const demoSection = document.getElementById('demo');
    if (demoSection) {
        demoSection.style.display = 'none';
    }
    
    // 로그인 후 섹션들 표시
    const loggedInSections = document.querySelectorAll('.logged-in-section');
    loggedInSections.forEach(section => {
        section.style.display = 'block';
    });
    
    // 메인 CTA 버튼들 변경
    const ctaRegisterBtn = document.getElementById('cta-register-btn');
    const ctaDemoBtn = document.getElementById('cta-demo-btn');
    const ctaDiagnosisBtn = document.getElementById('cta-diagnosis-btn');
    const ctaDashboardBtn = document.getElementById('cta-dashboard-btn');
    
    if (ctaRegisterBtn) ctaRegisterBtn.style.display = 'none';
    if (ctaDemoBtn) ctaDemoBtn.style.display = 'none';
    if (ctaDiagnosisBtn) ctaDiagnosisBtn.style.display = 'inline-block';
    if (ctaDashboardBtn) ctaDashboardBtn.style.display = 'inline-block';
    
    // 사용자 정보 추가 (드롭다운 메뉴로)
    const navbar = document.querySelector('.navbar-nav');
    if (navbar) {
        const userInfo = document.createElement('li');
        userInfo.className = 'nav-item dropdown';
        userInfo.id = 'userInfo';
        
        const profileImageHtml = userProfileImage 
            ? `<img src="${userProfileImage}" alt="프로필" class="rounded-circle me-2" style="width: 32px; height: 32px; object-fit: cover;">`
            : `<i class="fas fa-user-circle me-2" style="font-size: 24px;"></i>`;
            
        userInfo.innerHTML = `
            <a class="nav-link dropdown-toggle d-flex align-items-center" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                ${profileImageHtml}
                <span>${userName}님</span>
            </a>
            <ul class="dropdown-menu dropdown-menu-end">
                <li><a class="dropdown-item" href="#dashboard"><i class="fas fa-tachometer-alt me-2"></i>대시보드</a></li>
                <li><a class="dropdown-item" href="#diagnosis"><i class="fas fa-stethoscope me-2"></i>진단 기록</a></li>
                <li><a class="dropdown-item" href="#monitoring"><i class="fas fa-chart-line me-2"></i>실시간 모니터링</a></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item" href="#" onclick="logout()"><i class="fas fa-sign-out-alt me-2"></i>로그아웃</a></li>
            </ul>
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
    const kakaoBtn = document.querySelector('button[onclick="kakaoLogin()"]');
    
    if (loginBtn) loginBtn.style.display = 'inline-block';
    if (registerBtn) registerBtn.style.display = 'inline-block';
    if (kakaoBtn) kakaoBtn.style.display = 'inline-block';
    
    // 데모 섹션 다시 표시 (로그인 전에는 체험 모듈 표시)
    const demoSection = document.getElementById('demo');
    if (demoSection) {
        demoSection.style.display = 'block';
    }
    
    // 로그인 후 섹션들 숨기기
    const loggedInSections = document.querySelectorAll('.logged-in-section');
    loggedInSections.forEach(section => {
        section.style.display = 'none';
    });
    
    // 메인 CTA 버튼들 원래대로 복원
    const ctaRegisterBtn = document.getElementById('cta-register-btn');
    const ctaDemoBtn = document.getElementById('cta-demo-btn');
    const ctaDiagnosisBtn = document.getElementById('cta-diagnosis-btn');
    const ctaDashboardBtn = document.getElementById('cta-dashboard-btn');
    
    if (ctaRegisterBtn) ctaRegisterBtn.style.display = 'inline-block';
    if (ctaDemoBtn) ctaDemoBtn.style.display = 'inline-block';
    if (ctaDiagnosisBtn) ctaDiagnosisBtn.style.display = 'none';
    if (ctaDashboardBtn) ctaDashboardBtn.style.display = 'none';
}

// 카카오 로그인
async function kakaoLogin() {
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

// 카카오 로그인 콜백 처리
function handleKakaoCallback() {
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
        
        // 성공 메시지 표시
        alert('카카오 로그인이 완료되었습니다!');
    }
}

// 로그아웃
function logout() {
    const token = localStorage.getItem('authToken');
    
    fetch(`${API_BASE_URL}/api/auth/logout`, { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ sessionId: token })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
            localStorage.removeItem('authToken');
                showLoggedOutUI();
                console.log('로그아웃 성공');
            }
        })
        .catch(error => {
            console.error('로그아웃 오류:', error);
        localStorage.removeItem('authToken');
        showLoggedOutUI();
        });
}

// 로그인 모달 표시
function showLoginModal() {
    console.log('로그인 모달을 표시합니다.');
    
    const modalHtml = `
        <div class="modal fade" id="loginModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">로그인</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="loginForm">
                            <div class="mb-3">
                                <label for="loginEmail" class="form-label">이메일</label>
                                <input type="email" class="form-control" id="loginEmail" required>
                            </div>
                            <div class="mb-3">
                                <label for="loginPassword" class="form-label">비밀번호</label>
                                <input type="password" class="form-control" id="loginPassword" required>
                            </div>
                            <div class="d-grid">
                                <button type="submit" class="btn btn-primary">로그인</button>
                            </div>
                        </form>
                        <div class="text-center mt-3">
                            <button type="button" class="btn btn-link" onclick="showRegisterModal(); $('#loginModal').modal('hide');">회원가입</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 기존 모달 제거
    const existingModal = document.getElementById('loginModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 새 모달 추가
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // 모달 표시
    const modal = new bootstrap.Modal(document.getElementById('loginModal'));
    modal.show();
    
    // 폼 제출 이벤트
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
}

// 회원가입 모달 표시
function showRegisterModal() {
    console.log('회원가입 모달을 표시합니다.');
    
    const modalHtml = `
        <div class="modal fade" id="registerModal" tabindex="-1">
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">회원가입</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="registerForm">
                            <div class="mb-3">
                                <label for="registerName" class="form-label">이름</label>
                                <input type="text" class="form-control" id="registerName" required>
                            </div>
                            <div class="mb-3">
                                <label for="registerEmail" class="form-label">이메일</label>
                                <input type="email" class="form-control" id="registerEmail" required>
                            </div>
                            <div class="mb-3">
                                <label for="registerPassword" class="form-label">비밀번호</label>
                                <input type="password" class="form-control" id="registerPassword" required>
                            </div>
                            <div class="mb-3">
                                <label for="registerPhone" class="form-label">전화번호</label>
                                <input type="tel" class="form-control" id="registerPhone" required>
                            </div>
                            <div class="mb-3">
                                <label for="registerCompany" class="form-label">회사명 (선택)</label>
                                <input type="text" class="form-control" id="registerCompany">
                            </div>
                            <div class="mb-3 form-check">
                                <input type="checkbox" class="form-check-input" id="marketingAgree">
                                <label class="form-check-label" for="marketingAgree">
                                    마케팅 정보 수신 동의
                                </label>
                            </div>
                            <div class="d-grid">
                                <button type="submit" class="btn btn-primary">회원가입</button>
                            </div>
                        </form>
                        <div class="text-center mt-3">
                            <button type="button" class="btn btn-link" onclick="showLoginModal(); $('#registerModal').modal('hide');">로그인</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 기존 모달 제거
    const existingModal = document.getElementById('registerModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 새 모달 추가
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // 모달 표시
    const modal = new bootstrap.Modal(document.getElementById('registerModal'));
    modal.show();
    
    // 폼 제출 이벤트
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
}

// 로그인 처리
function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            localStorage.setItem('authToken', data.sessionId);
            currentUser = data.user;
            updateLoginStatus();
            $('#loginModal').modal('hide');
            alert('로그인 성공!');
        } else {
            alert(data.message || '로그인 실패');
        }
    })
    .catch(error => {
        console.error('로그인 오류:', error);
        alert('로그인 중 오류가 발생했습니다.');
    });
}

// 회원가입 처리
function handleRegister(event) {
    event.preventDefault();
    
    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const phone = document.getElementById('registerPhone').value;
    const company = document.getElementById('registerCompany').value;
    const marketing_agree = document.getElementById('marketingAgree').checked;
    
    fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name, email, password, phone, company, marketing_agree })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            $('#registerModal').modal('hide');
            alert('회원가입 성공! 로그인해주세요.');
            showLoginModal();
        } else {
            alert(data.message || '회원가입 실패');
        }
    })
    .catch(error => {
        console.error('회원가입 오류:', error);
        alert('회원가입 중 오류가 발생했습니다.');
    });
}

// 이벤트 리스너 설정
function setupEventListeners() {
    console.log('이벤트 리스너를 설정합니다.');
}

// 전역 함수로 등록
window.showLoginModal = showLoginModal;
window.showRegisterModal = showRegisterModal;
window.updateLoginStatus = updateLoginStatus;
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

// 전역 함수로 등록
window.showLoggedInUI = showLoggedInUI;
window.showLoggedOutUI = showLoggedOutUI;
window.logout = logout;
window.checkLoginSuccess = checkLoginSuccess;
window.startDiagnosis = startDiagnosis;
window.goToDashboard = goToDashboard;
window.toggleMonitoring = toggleMonitoring;
window.stopMonitoring = stopMonitoring;
window.viewDiagnosisHistory = viewDiagnosisHistory;
window.saveMonitoringSettings = saveMonitoringSettings;
