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
    const registerBtn = document.querySelector('button[onclick="enhancedRegistration.show()"]');
    const kakaoBtn = document.querySelector('button[onclick="kakaoLogin()"]');
    
    if (loginBtn) loginBtn.style.display = 'none';
    if (registerBtn) registerBtn.style.display = 'none';
    // if (kakaoBtn) kakaoBtn.style.display = 'none';
    
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
    
    // 로그인 후 환영 메시지 표시
    showWelcomeMessage(userName);
}

// 환영 메시지 표시
function showWelcomeMessage(userName) {
    // 기존 환영 메시지 제거
    const existingWelcome = document.getElementById('welcomeMessage');
    if (existingWelcome) {
        existingWelcome.remove();
    }
    
    // 히어로 섹션에 환영 메시지 추가
    const heroSection = document.getElementById('home');
    if (heroSection) {
        const welcomeHTML = `
            <div id="welcomeMessage" class="alert alert-success alert-dismissible fade show mb-4" role="alert">
                <div class="d-flex align-items-center">
                    <i class="fas fa-check-circle me-2"></i>
                    <div>
                        <strong>환영합니다, ${userName}님!</strong> 
                        Signalcraft AI 진단 서비스를 이용하실 수 있습니다.
                    </div>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        const container = heroSection.querySelector('.container .row');
        if (container) {
            container.insertAdjacentHTML('afterbegin', welcomeHTML);
        }
    }
    
    // 로그인 후 개인화된 콘텐츠 표시
    showPersonalizedContent();
}

// 개인화된 콘텐츠 표시
function showPersonalizedContent() {
    // 기존 개인화 콘텐츠 제거
    const existingPersonalized = document.getElementById('personalizedContent');
    if (existingPersonalized) {
        existingPersonalized.remove();
    }
    
    // 개인화된 섹션 추가
    const personalizedHTML = `
        <div id="personalizedContent" class="container mt-5">
            <div class="row">
                <div class="col-12">
                    <div class="card border-0 shadow-sm">
                        <div class="card-header bg-primary text-white">
                            <h5 class="mb-0"><i class="fas fa-user-check me-2"></i>개인 대시보드</h5>
                        </div>
                        <div class="card-body">
                            <div class="row g-4">
                                <div class="col-md-4">
                                    <div class="text-center">
                                        <div class="bg-primary bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 80px; height: 80px;">
                                            <i class="fas fa-brain text-primary" style="font-size: 2rem;"></i>
                                        </div>
                                        <h6>AI 진단 시작</h6>
                                        <p class="text-muted small">압축기 소리를 분석하여 상태를 진단합니다.</p>
                                        <button class="btn btn-primary btn-sm" onclick="startDiagnosis()">
                                            <i class="fas fa-play me-1"></i>진단 시작
                                        </button>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="text-center">
                                        <div class="bg-success bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 80px; height: 80px;">
                                            <i class="fas fa-chart-line text-success" style="font-size: 2rem;"></i>
                                        </div>
                                        <h6>실시간 모니터링</h6>
                                        <p class="text-muted small">24시간 압축기 상태를 감시합니다.</p>
                                        <button class="btn btn-success btn-sm" onclick="showMonitoring()">
                                            <i class="fas fa-eye me-1"></i>모니터링
                                        </button>
                                    </div>
                                </div>
                                <div class="col-md-4">
                                    <div class="text-center">
                                        <div class="bg-info bg-opacity-10 rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 80px; height: 80px;">
                                            <i class="fas fa-history text-info" style="font-size: 2rem;"></i>
                                        </div>
                                        <h6>진단 이력</h6>
                                        <p class="text-muted small">과거 진단 결과를 확인할 수 있습니다.</p>
                                        <button class="btn btn-info btn-sm" onclick="showHistory()">
                                            <i class="fas fa-list me-1"></i>이력 보기
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // 히어로 섹션 다음에 추가
    const heroSection = document.getElementById('home');
    if (heroSection) {
        heroSection.insertAdjacentHTML('afterend', personalizedHTML);
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
    
    // 네비게이션 바 완전 재생성 및 고정
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        navbar.innerHTML = `
            <div class="container">
                <a class="navbar-brand" href="#home">
                    <i class="fas fa-shield-alt me-2"></i>Signalcraft
                </a>
                <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                    <span class="navbar-toggler-icon"></span>
                </button>
                <div class="navbar-collapse show" id="navbarNav" style="display: flex !important; width: 100% !important;">
                    <ul class="navbar-nav ms-auto" style="display: flex !important; flex-direction: row !important; width: auto !important;">
                        <li class="nav-item">
                            <a class="nav-link" href="#home">홈</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#features">기능</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#pricing">요금제</a>
                        </li>
                        <li class="nav-item">
                            <a class="nav-link" href="#demo">체험</a>
                        </li>
                        <li class="nav-item">
                            <button class="btn btn-outline-light ms-2" onclick="showLoginModal()">로그인</button>
                        </li>
                        <li class="nav-item">
                            <button class="btn btn-warning ms-2" onclick="kakaoLogin()"><i class="fab fa-kickstarter me-1"></i>카카오 로그인</button>
                        </li>
                        <li class="nav-item">
                            <button class="btn btn-light ms-2" onclick="enhancedRegistration.show()">회원가입</button>
                        </li>
                    </ul>
                </div>
            </div>
        `;
        console.log('네비게이션 바 완전 재생성 및 고정 완료');
    }
    
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
        
        // 개선된 성공 화면 표시
        showLoginSuccessModal();
    }
}

// 로그인 성공 모달 표시
function showLoginSuccessModal() {
    // 기존 모달 제거
    const existingModal = document.getElementById('loginSuccessModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // 성공 모달 생성
    const modalHTML = `
        <div class="modal fade" id="loginSuccessModal" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content border-0 shadow-lg">
                    <div class="modal-body text-center p-5">
                        <div class="mb-4">
                            <div class="success-animation mb-3">
                                <i class="fas fa-check-circle text-success" style="font-size: 4rem;"></i>
                            </div>
                            <h3 class="text-success mb-3">로그인 성공!</h3>
                            <p class="text-muted mb-4">Signalcraft AI 진단 서비스에 오신 것을 환영합니다.</p>
                        </div>
                        
                        <div class="row g-3 mb-4">
                            <div class="col-6">
                                <div class="card border-0 bg-light">
                                    <div class="card-body text-center">
                                        <i class="fas fa-brain text-primary mb-2" style="font-size: 2rem;"></i>
                                        <h6>AI 진단</h6>
                                        <small class="text-muted">압축기 상태 분석</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-6">
                                <div class="card border-0 bg-light">
                                    <div class="card-body text-center">
                                        <i class="fas fa-chart-line text-success mb-2" style="font-size: 2rem;"></i>
                                        <h6>실시간 모니터링</h6>
                                        <small class="text-muted">24시간 감시</small>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="d-grid gap-2">
                            <button class="btn btn-primary btn-lg" onclick="startDiagnosis()">
                                <i class="fas fa-play me-2"></i>진단 시작하기
                            </button>
                            <button class="btn btn-outline-secondary" onclick="closeLoginSuccessModal()">
                                나중에 시작하기
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // 모달 표시
    const modal = new bootstrap.Modal(document.getElementById('loginSuccessModal'));
    modal.show();
    
    // 애니메이션 효과
    setTimeout(() => {
        const checkIcon = document.querySelector('#loginSuccessModal .fa-check-circle');
        if (checkIcon) {
            checkIcon.style.animation = 'bounceIn 0.6s ease-out';
        }
    }, 100);
}

// 로그인 성공 모달 닫기
function closeLoginSuccessModal() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('loginSuccessModal'));
    if (modal) {
        modal.hide();
    }
}

// 진단 시작하기
function startDiagnosis() {
    closeLoginSuccessModal();
    // 진단 페이지로 이동하거나 진단 모달 표시
    showDiagnosisModal();
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
                                <label for="loginEmail" class="form-label">사용자명 또는 이메일</label>
                                <input type="text" class="form-control" id="loginEmail" placeholder="사용자명 또는 이메일을 입력하세요" required>
                            </div>
                            <div class="mb-3">
                                <label for="loginPassword" class="form-label">비밀번호</label>
                                <input type="password" class="form-control" id="loginPassword" placeholder="비밀번호를 입력하세요" required>
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
    
    // 간단한 클라이언트 사이드 로그인 검증
    if (email === 'admin' && password === 'admin123') {
        localStorage.setItem('authToken', 'demo_token_123');
        currentUser = {
            id: 1,
            email: 'admin',
            name: '관리자',
            role: 'admin'
        };
            updateLoginStatus();
            $('#loginModal').modal('hide');
        alert('로그인 성공! 관리자 대시보드로 이동합니다.');
        // 관리자 대시보드로 이동
        window.location.href = '/admin/';
        } else {
        alert('잘못된 사용자명 또는 비밀번호입니다.\n\n데모용 계정:\n사용자명: admin\n비밀번호: admin123');
        }
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
