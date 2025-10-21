// static/js/ui/navbar-renderer.js
class NavbarRenderer {
    showLoggedInUI(user) {
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
                
            // 역할에 따른 메뉴 구성
            let menuItems = '';
            if (user.role === 'admin') {
                menuItems = `
                    <li><a class="dropdown-item" href="/admin/"><i class="fas fa-cog me-2"></i>관리자 대시보드</a></li>
                    <li><a class="dropdown-item" href="#dashboard"><i class="fas fa-tachometer-alt me-2"></i>사용자 대시보드</a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li><a class="dropdown-item" href="#diagnosis"><i class="fas fa-stethoscope me-2"></i>진단 기록</a></li>
                    <li><a class="dropdown-item" href="#monitoring"><i class="fas fa-chart-line me-2"></i>실시간 모니터링</a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li><a class="dropdown-item" href="#" onclick="logout()"><i class="fas fa-sign-out-alt me-2"></i>로그아웃</a></li>
                `;
            } else {
                menuItems = `
                    <li><a class="dropdown-item" href="#dashboard"><i class="fas fa-tachometer-alt me-2"></i>내 대시보드</a></li>
                    <li><a class="dropdown-item" href="#diagnosis"><i class="fas fa-stethoscope me-2"></i>진단 기록</a></li>
                    <li><a class="dropdown-item" href="#monitoring"><i class="fas fa-chart-line me-2"></i>실시간 모니터링</a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li><a class="dropdown-item" href="#" onclick="showProfile()"><i class="fas fa-user-cog me-2"></i>계정 설정</a></li>
                    <li><a class="dropdown-item" href="#" onclick="logout()"><i class="fas fa-sign-out-alt me-2"></i>로그아웃</a></li>
                `;
            }

            userInfo.innerHTML = `
                <a class="nav-link dropdown-toggle d-flex align-items-center" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
                    ${profileImageHtml}
                    <span>${userName}님</span>
                    ${user.role === 'admin' ? '<span class="badge bg-warning text-dark ms-2">관리자</span>' : ''}
                </a>
                <ul class="dropdown-menu dropdown-menu-end">
                    ${menuItems}
                </ul>
            `;
            navbar.appendChild(userInfo);
        }
        
        // 로그인 후 환영 메시지 표시
        this.showWelcomeMessage(userName);
    }

    // 환영 메시지 표시
    showWelcomeMessage(userName) {
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
        this.showPersonalizedContent();
    }

    // 개인화된 콘텐츠 표시
    showPersonalizedContent() {
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
    showLoggedOutUI() {
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
}

// 프로필 설정 함수 (일반 사용자용)
function showProfile() {
    alert('프로필 설정 기능은 준비 중입니다.');
}