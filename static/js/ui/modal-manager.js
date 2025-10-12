// static/js/ui/modal-manager.js
class ModalManager {
    showLoginModal() {
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

    showRegisterModal() {
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
}

// 회원가입 처리
async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('registerName').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    const phone = document.getElementById('registerPhone').value;
    const full_name = document.getElementById('registerCompany').value; // 회사명을 full_name으로 사용
    const marketing_agree = document.getElementById('marketingAgree').checked;
    
    // 간단한 검증
    if (!username || !email || !password) {
        alert('사용자명, 이메일, 비밀번호는 필수입니다.');
        return;
    }
    
    if (password.length < 6) {
        alert('비밀번호는 최소 6자 이상이어야 합니다.');
        return;
    }
    
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ 
                username, 
                email, 
                password, 
                phone, 
                full_name, 
                marketing_agree 
            })
        });

        const data = await response.json();

        if (data.success) {
            // 모달 닫기 (Bootstrap 5 방식)
            const modal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
            if (modal) {
                modal.hide();
            }
            alert('회원가입 성공! 로그인해주세요.');
            showLoginModal();
        } else {
            alert(data.message || '회원가입 실패');
        }
    } catch (error) {
        console.error('회원가입 오류:', error);
        alert('회원가입 중 오류가 발생했습니다.');
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