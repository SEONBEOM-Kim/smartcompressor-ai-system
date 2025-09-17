// Signalcraft 웹 애플리케이션 JavaScript

// API 기본 URL
const API_BASE_URL = 'http://3.39.124.0:8000';

// 전역 변수
let currentUser = null;
let authToken = null;

// DOM 로드 완료 시 실행
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadPricingPlans();
    initializeHeroChart();
});

// 앱 초기화
function initializeApp() {
    // URL 파라미터에서 카카오 로그인 정보 확인
    const urlParams = new URLSearchParams(window.location.search);
    const loginStatus = urlParams.get('login');
    const token = urlParams.get('token');
    const userId = urlParams.get('user_id');
    const email = urlParams.get('email');
    
    if (loginStatus === 'success' && token && userId && email) {
        // 카카오 로그인 성공 처리
        currentUser = {
            id: userId,
            email: email,
            name: '카카오 사용자'
        };
        authToken = token;
        
        // 로컬 스토리지에 저장
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        localStorage.setItem('authToken', authToken);
        
        // UI 업데이트
        updateUIForLoggedInUser();
        
        // URL에서 파라미터 제거
        window.history.replaceState({}, document.title, window.location.pathname);
        
        showNotification('카카오 로그인에 성공했습니다!', 'success');
    } else {
        // 로컬 스토리지에서 사용자 정보 확인
        const savedUser = localStorage.getItem('currentUser');
        const savedToken = localStorage.getItem('authToken');
        
        if (savedUser && savedToken) {
//             currentUser = JSON.parse(savedUser);
            authToken = savedToken;
            updateUIForLoggedInUser();
        }
    }
    
    // 스크롤 애니메이션 설정
    setupScrollAnimations();
}

// 이벤트 리스너 설정
function setupEventListeners() {
    // 로그인 폼
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    // 회원가입 폼
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    // 스크롤 이벤트
    window.addEventListener('scroll', handleScroll);
}

// 로그인 처리
async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        if (response.ok) {
        const data = await response.json();

            currentUser = data.user || {email: email};
            updateUIForLoggedInUser();
            currentUser = data.user;
            authToken = data.access_token;
            
            // 로컬 스토리지에 저장
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            localStorage.setItem('authToken', authToken);
            
	    // 🚀 대시보드 리다이렉트 추가
if (data.success) {
    // 모달 먼저 닫기
    const loginModal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
    if (loginModal) loginModal.hide();
    
    // 성공 알림 (짧게)
    showNotification('로그인 성공!', 'success');
    
    // 즉시 리다이렉트
    setTimeout(() => {
        window.location.href = '/dashboard';
    }, 500);
}
            // UI 업데이트
            updateUIForLoggedInUser();
            
            // 모달 닫기
            const loginModal = bootstrap.Modal.getInstance(document.getElementById('loginModal'));
            loginModal.hide();
            
            currentUser = data.user || {email: email};
localStorage.setItem('currentUser', JSON.stringify(currentUser));
localStorage.setItem('authToken', data.token || 'fake-token');
showNotification('로그인에 성공했습니다!', 'success');
updateUIForLoggedInUser();
        } else {
            const error = await response.json();
            showNotification(error.detail || '로그인에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showNotification('로그인 중 오류가 발생했습니다.', 'error');
    }
}

        // 회원가입 처리
async function handleRegister(e) {
    e.preventDefault();

    const name = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const phone = document.getElementById('registerPhone').value;
    const company = document.getElementById('registerCompany').value;
    const password = document.getElementById('registerPassword').value;
    const marketing_agree = document.getElementById('marketingAgree').checked;

    try {
        const response = await fetch(`${API_BASE_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, phone, company, password, marketing_agree })
        });

        if (response.ok) {
        const data = await response.json();
            showNotification('회원가입이 완료되었습니다! 첫 달 9,900원 혜택이 적용되었습니다.', 'success');
            
            // 모달 닫기
            const registerModal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
            registerModal.hide();
            
            // 로그인 모달로 전환
            showLoginModal();
        } else {
            const error = await response.json();
            showNotification(error.detail || '회원가입에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('Register error:', error);
        showNotification('회원가입 중 오류가 발생했습니다.', 'error');
    }
}

// 카카오 로그인
function loginWithKakao() {
    // 카카오 로그인 URL로 리다이렉트
    window.location.href = `${API_BASE_URL}/auth/kakao`;
}

// 로그인 모달 표시
function showLoginModal() {
    const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
    loginModal.show();
}

// 회원가입 모달 표시
function showRegisterModal() {
    const registerModal = new bootstrap.Modal(document.getElementById('registerModal'));
    registerModal.show();
}

// 로그아웃
function logout() {
    currentUser = null;
    authToken = null;
    localStorage.removeItem('currentUser');
    localStorage.removeItem('authToken');
    updateUIForLoggedOutUser();
    showNotification('로그아웃되었습니다.', 'info');
}

// 로그인된 사용자 UI 업데이트
function updateUIForLoggedInUser() {
    // 관리자 계정 체크
    if (currentUser && currentUser.email === "admin@signalcraft.kr") {
        // 관리자 대시보드로 리다이렉트
        window.location.href = "/admin";
        return;
    }
    const navbar = document.querySelector('.navbar-nav');
    if (navbar && currentUser) {
        navbar.innerHTML = `
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
            <li class="nav-item dropdown">
                <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown">
                    <i class="fas fa-user me-1"></i>${currentUser.email}
                </a>
                <ul class="dropdown-menu">
                    <li><a class="dropdown-item" href="#" onclick="showDashboard()">
                        <i class="fas fa-tachometer-alt me-2"></i>대시보드
                    </a></li>
                    <li><a class="dropdown-item" href="#" onclick="showSubscription()">
                        <i class="fas fa-credit-card me-2"></i>구독 관리
                    </a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li><a class="dropdown-item" href="#" onclick="logout()">
                        <i class="fas fa-sign-out-alt me-2"></i>로그아웃
                    </a></li>
                </ul>
            </li>
        `;
    }
}

// 로그아웃된 사용자 UI 업데이트
function updateUIForLoggedOutUser() {
    const navbar = document.querySelector('.navbar-nav');
    if (navbar) {
        navbar.innerHTML = `
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
                <button class="btn btn-light ms-2" onclick="showRegisterModal()">회원가입</button>
            </li>
        `;
    }
}

// 요금제 선택
function selectPlan(planType) {
    if (!currentUser) {
        showRegisterModal();
        return;
    }
    
    const plans = {
        essential: { name: '에센셜', price: 29000 },
        standard: { name: '스탠다드', price: 49000 },
        premium: { name: '프리미엄', price: 99000 }
    };
    
    const selectedPlan = plans[planType];
    if (selectedPlan) {
        showPaymentModal(selectedPlan);
    }
}

// 결제 모달 표시
function showPaymentModal(plan) {
    const paymentContent = document.getElementById('payment-content');
    if (paymentContent) {
        paymentContent.innerHTML = `
            <div class="text-center">
                <h5>${plan.name} 플랜</h5>
                <div class="price-display mb-4">
                    <span class="price-amount">${plan.price.toLocaleString()}</span>
                    <span class="price-unit">원/월</span>
            </div>
                <p class="text-muted">첫 달 9,900원 혜택이 적용됩니다!</p>
                <div class="d-grid gap-2">
                    <button class="btn btn-primary" onclick="processPayment('${plan.name}', ${plan.price})">
                        <i class="fas fa-credit-card me-2"></i>결제하기
                    </button>
                    <button class="btn btn-outline-secondary" data-bs-dismiss="modal">
                        취소
                    </button>
            </div>
        </div>
    `;
    
        const paymentModal = new bootstrap.Modal(document.getElementById('paymentModal'));
        paymentModal.show();
    }
}

// 카카오페이 결제 처리
async function processPayment(planName, price) {
    try {
        // 결제 준비
        const response = await fetch(`${API_BASE_URL}/payment/ready`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                plan_type: planName.toLowerCase(),
                user_email: currentUser ? currentUser.email : 'test@example.com'
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.success && data.payment_url) {
                // 카카오페이 결제 페이지로 리다이렉트
                window.location.href = data.payment_url;
            } else {
                showNotification('결제 준비에 실패했습니다.', 'error');
            }
        } else {
            const error = await response.json();
            showNotification(error.detail || '결제 준비에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('Payment error:', error);
        showNotification('결제 중 오류가 발생했습니다.', 'error');
    }
}

// 대시보드 표시
async function showDashboard() {
    if (!currentUser) {
        showLoginModal();
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/user/dashboard`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
        const data = await response.json();
            displayDashboard(data);
        } else {
            showNotification('대시보드 로드에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('Dashboard error:', error);
        showNotification('대시보드 로드 중 오류가 발생했습니다.', 'error');
    }
}

// 대시보드 표시
function displayDashboard(data) {
    const dashboardContent = document.getElementById('dashboard-content');
    if (dashboardContent) {
        dashboardContent.innerHTML = `
            <div class="row">
                <div class="col-md-4">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title">관리 중인 냉동고</h5>
                            <h2 class="text-primary">${data.equipment_count || 0}</h2>
                    </div>
                </div>
            </div>
                <div class="col-md-4">
                    <div class="card text-center">
                        <div class="card-body">
                            <h5 class="card-title">이번 달 분석</h5>
                            <h2 class="text-success">${data.analysis_count || 0}</h2>
                </div>
            </div>
        </div>
                <div class="col-md-4">
                    <div class="card text-center">
                    <div class="card-body">
                            <h5 class="card-title">구독 상태</h5>
                            <h6 class="text-info">${data.subscription_plan || '없음'}</h6>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5>최근 분석 결과</h5>
                            </div>
                        <div class="card-body">
                            <p class="text-muted">아직 분석 결과가 없습니다. 냉동고를 등록하고 분석을 시작해보세요!</p>
                    </div>
                </div>
            </div>
        </div>
    `;
        
        const dashboardModal = new bootstrap.Modal(document.getElementById('dashboardModal'));
        dashboardModal.show();
    }
}

// 구독 관리 표시
async function showSubscription() {
    if (!currentUser) {
        showLoginModal();
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/user/subscription`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
        const data = await response.json();
            displaySubscription(data);
        } else {
            showNotification('구독 정보 로드에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('Subscription error:', error);
        showNotification('구독 정보 로드 중 오류가 발생했습니다.', 'error');
    }
}

// 구독 관리 표시
function displaySubscription(data) {
    const subscriptionContent = document.getElementById('subscription-content');
    if (subscriptionContent) {
        const subscription = data.subscription;
        
        if (subscription) {
            subscriptionContent.innerHTML = `
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">현재 구독 정보</h5>
                        <div class="row">
                            <div class="col-md-6">
                                <p><strong>플랜:</strong> ${subscription.plan_type || '없음'}</p>
                                <p><strong>가격:</strong> ${subscription.amount ? subscription.amount.toLocaleString() + '원/월' : '없음'}</p>
                    </div>
                            <div class="col-md-6">
                                <p><strong>다음 결제일:</strong> ${subscription.next_billing_date || '없음'}</p>
                                <p><strong>상태:</strong> <span class="badge bg-success">${subscription.status || '활성'}</span></p>
                </div>
            </div>
                        <div class="mt-3">
                            <button class="btn btn-outline-primary me-2" onclick="selectPlan('standard')">
                                플랜 변경
                </button>
                            <button class="btn btn-outline-danger" onclick="cancelSubscription()">
                    구독 취소
                </button>
                        </div>
                    </div>
            </div>
        `;
    } else {
            subscriptionContent.innerHTML = `
                <div class="card">
                    <div class="card-body text-center">
                        <h5 class="card-title">구독 정보가 없습니다</h5>
                        <p class="text-muted">아직 구독하지 않으셨습니다. 플랜을 선택하여 구독을 시작하세요.</p>
                        <button class="btn btn-primary" onclick="selectPlan('standard')">
                            구독 시작하기
                </button>
                    </div>
            </div>
        `;
    }
        
        const subscriptionModal = new bootstrap.Modal(document.getElementById('subscriptionModal'));
        subscriptionModal.show();
    }
}

// 구독 취소
async function cancelSubscription() {
    if (!confirm('정말로 구독을 취소하시겠습니까?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/payment/subscription/${currentUser.id}/cancel`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            showNotification('구독이 취소되었습니다.', 'success');
            // 구독 정보 새로고침
            showSubscription();
        } else {
            const error = await response.json();
            showNotification(error.detail || '구독 취소에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('Subscription cancellation error:', error);
        showNotification('구독 취소 중 오류가 발생했습니다.', 'error');
    }
}

// 요금제 로드
async function loadPricingPlans() {
    try {
        const response = await fetch(`${API_BASE_URL}/pricing`);
        if (response.ok) {
            const data = await response.json();
            // 요금제 데이터가 필요하면 여기서 처리
        }
    } catch (error) {
        console.error('Pricing plans load error:', error);
    }
}

// 히어로 차트 초기화
function initializeHeroChart() {
    const ctx = document.getElementById('hero-chart');
    if (ctx) {
    new Chart(ctx, {
        type: 'line',
        data: {
                labels: ['1일', '2일', '3일', '4일', '5일', '6일', '7일'],
            datasets: [{
                    label: '위험도 점수',
                    data: [25, 30, 28, 35, 32, 29, 25],
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4,
                    fill: true
            }]
        },
        options: {
            responsive: true,
                maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                }
            }
        }
    });
}
}

// 스크롤 애니메이션 설정
function setupScrollAnimations() {
    const animateElements = document.querySelectorAll('.feature-card, .pricing-card');
    animateElements.forEach(el => {
        el.classList.add('scroll-animate');
    });
}

// 스크롤 이벤트 처리
function handleScroll() {
    const animateElements = document.querySelectorAll('.scroll-animate');
    animateElements.forEach(el => {
        const elementTop = el.getBoundingClientRect().top;
        const elementVisible = 150;
        
        if (elementTop < window.innerHeight - elementVisible) {
            el.classList.add('animate');
        }
    });
}

// 섹션으로 스크롤
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

// 알림 표시
function showNotification(message, type = 'info') {
    // 간단한 알림 구현
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // 5초 후 자동 제거
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// 유틸리티 함수들
function formatDate(date) {
    return new Date(date).toLocaleDateString('ko-KR');
}

function formatCurrency(amount) {
    return amount.toLocaleString() + '원';
}

// API 호출 헬퍼
async function apiCall(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (authToken) {
        defaultOptions.headers['Authorization'] = `Bearer ${authToken}`;
    }
    
    const finalOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, finalOptions);
        return response;
    } catch (error) {
        console.error('API call error:', error);
        throw error;
    }
}
