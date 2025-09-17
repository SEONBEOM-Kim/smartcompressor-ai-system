// 인증 관리자 클래스
class AuthManager {
    constructor() {
        this.currentUser = null;
        this.isLoggedIn = false;
        this.init();
    }
    
    init() {
        // 로컬 스토리지에서 사용자 정보 확인
        this.loadUserFromStorage();
        this.updateUI();
    }
    
    loadUserFromStorage() {
        const userData = localStorage.getItem('currentUser');
        if (userData) {
            try {
                this.currentUser = JSON.parse(userData);
                this.isLoggedIn = true;
            } catch (e) {
                console.error('사용자 데이터 파싱 오류:', e);
                this.clearUserData();
            }
        }
    }
    
    saveUserToStorage(userData) {
        localStorage.setItem('currentUser', JSON.stringify(userData));
        this.currentUser = userData;
        this.isLoggedIn = true;
        this.updateUI();
    }
    
    clearUserData() {
        localStorage.removeItem('currentUser');
        this.currentUser = null;
        this.isLoggedIn = false;
        this.updateUI();
    }
    
    updateUI() {
        // 로그인/회원가입 버튼 표시/숨김
        this.toggleAuthButtons();
        
        // AI 진단 모듈 표시/숨김
        this.toggleAIDiagnosisModule();
        
        // 고객 대시보드 표시/숨김
        this.toggleCustomerDashboard();
        
        // 사용자 정보 표시
        this.updateUserInfo();
    }
    
    toggleAuthButtons() {
        const loginBtn = document.querySelector('[onclick="showLoginModal()"]');
        const registerBtn = document.querySelector('[onclick="showRegisterModal()"]');
        const logoutBtn = document.getElementById('logoutBtn');
        
        if (this.isLoggedIn) {
            // 로그인 상태: 로그인/회원가입 버튼 숨김, 로그아웃 버튼 표시
            if (loginBtn) loginBtn.style.display = 'none';
            if (registerBtn) registerBtn.style.display = 'none';
            
            // 로그아웃 버튼이 없으면 생성
            if (!logoutBtn) {
                this.createLogoutButton();
            } else {
                logoutBtn.style.display = 'inline-block';
            }
        } else {
            // 비로그인 상태: 로그인/회원가입 버튼 표시, 로그아웃 버튼 숨김
            if (loginBtn) loginBtn.style.display = 'inline-block';
            if (registerBtn) registerBtn.style.display = 'inline-block';
            if (logoutBtn) logoutBtn.style.display = 'none';
        }
    }
    
    createLogoutButton() {
        const navbar = document.querySelector('.navbar-nav');
        if (navbar) {
            const logoutBtn = document.createElement('button');
            logoutBtn.id = 'logoutBtn';
            logoutBtn.className = 'btn btn-outline-light me-2';
            logoutBtn.innerHTML = '<i class="fas fa-sign-out-alt me-1"></i>로그아웃';
            logoutBtn.onclick = () => this.logout();
            navbar.appendChild(logoutBtn);
        }
    }
    
    toggleAIDiagnosisModule() {
        const aiModule = document.getElementById('ai-diagnosis-section');
        if (aiModule) {
            if (this.isLoggedIn) {
                // 로그인 후: 체험용 AI 숨김
                aiModule.style.display = 'none';
            } else {
                // 로그인 전: 체험용 AI 표시
                aiModule.style.display = 'block';
            }
        }
    }
    
    toggleCustomerDashboard() {
        const dashboardSection = document.getElementById('customer-dashboard-section');
        if (dashboardSection) {
            if (this.isLoggedIn) {
                // 로그인 후: 고객 대시보드 표시
                dashboardSection.style.display = 'block';
            } else {
                // 로그인 전: 고객 대시보드 숨김
                dashboardSection.style.display = 'none';
            }
        }
    }
    
    updateUserInfo() {
        const userInfoElement = document.getElementById('userInfo');
        if (userInfoElement) {
            if (this.isLoggedIn && this.currentUser) {
                userInfoElement.innerHTML = `
                    <span class="text-white">
                        <i class="fas fa-user me-1"></i>
                        ${this.currentUser.name || this.currentUser.email}
                    </span>
                `;
                userInfoElement.style.display = 'inline-block';
            } else {
                userInfoElement.style.display = 'none';
            }
        }
    }
    
    login(userData) {
        this.saveUserToStorage(userData);
        this.showNotification('로그인되었습니다.', 'success');
    }
    
    logout() {
        this.clearUserData();
        this.showNotification('로그아웃되었습니다.', 'info');
        // 페이지 새로고침
        window.location.reload();
    }
    
    showNotification(message, type = 'info') {
        const alertClass = type === 'error' ? 'alert-danger' : 
                          type === 'success' ? 'alert-success' : 
                          type === 'warning' ? 'alert-warning' : 'alert-info';
        
        const notification = document.createElement('div');
        notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // 3초 후 자동 제거
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
}

// 전역 인증 관리자 인스턴스
window.authManager = new AuthManager();
