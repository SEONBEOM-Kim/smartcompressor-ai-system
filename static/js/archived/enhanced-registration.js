// 향상된 회원가입 시스템
class EnhancedRegistration {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 4;
        this.formData = {};
        this.init();
    }
    
    init() {
        this.createRegistrationModal();
        this.setupEventListeners();
    }
    
    createRegistrationModal() {
        // 기존 모달 제거
        const existingModal = document.getElementById('enhancedRegisterModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        const modalHTML = `
            <div class="modal fade" id="enhancedRegisterModal" tabindex="-1" data-bs-backdrop="static" data-bs-keyboard="false">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header border-0 pb-0">
                            <h5 class="modal-title">
                                <i class="fas fa-user-plus me-2 text-primary"></i>
                                Signalcraft 회원가입
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body p-4">
                            <!-- 진행률 표시 -->
                            <div class="progress mb-4" style="height: 8px;">
                                <div id="registrationProgress" class="progress-bar bg-primary" role="progressbar" style="width: 25%"></div>
                            </div>
                            
                            <!-- 단계 표시 -->
                            <div class="d-flex justify-content-between mb-4">
                                <span class="badge bg-primary">1. 기본 정보</span>
                                <span class="badge bg-light text-dark">2. 추가 정보</span>
                                <span class="badge bg-light text-dark">3. 서비스 설정</span>
                                <span class="badge bg-light text-dark">4. 약관 동의</span>
                            </div>
                            
                            <!-- 폼 컨테이너 -->
                            <div id="registrationFormContainer">
                                <!-- 단계별 폼이 여기에 동적으로 생성됩니다 -->
                            </div>
                            
                            <!-- 네비게이션 버튼 -->
                            <div class="d-flex justify-content-between mt-4">
                                <button id="prevBtn" class="btn btn-outline-secondary" onclick="enhancedRegistration.previousStep()" style="display: none;">
                                    <i class="fas fa-arrow-left me-1"></i>이전
                                </button>
                                <div class="ms-auto">
                                    <button id="nextBtn" class="btn btn-primary" onclick="enhancedRegistration.nextStep()">
                                        다음 <i class="fas fa-arrow-right ms-1"></i>
                                    </button>
                                    <button id="submitBtn" class="btn btn-success" onclick="enhancedRegistration.submitRegistration()" style="display: none;">
                                        <i class="fas fa-check me-1"></i>회원가입 완료
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHTML);
    }
    
    setupEventListeners() {
        // 실시간 유효성 검사
        document.addEventListener('input', (e) => {
            if (e.target.matches('#enhancedRegisterModal input, #enhancedRegisterModal select')) {
                this.validateField(e.target);
            }
        });
    }
    
    show() {
        const modal = new bootstrap.Modal(document.getElementById('enhancedRegisterModal'));
        modal.show();
        this.renderStep(1);
    }
    
    renderStep(step) {
        const container = document.getElementById('registrationFormContainer');
        const progress = document.getElementById('registrationProgress');
        const prevBtn = document.getElementById('prevBtn');
        const nextBtn = document.getElementById('nextBtn');
        const submitBtn = document.getElementById('submitBtn');
        
        // 진행률 업데이트
        progress.style.width = `${(step / this.totalSteps) * 100}%`;
        
        // 버튼 상태 업데이트
        prevBtn.style.display = step > 1 ? 'block' : 'none';
        nextBtn.style.display = step < this.totalSteps ? 'block' : 'none';
        submitBtn.style.display = step === this.totalSteps ? 'block' : 'none';
        
        // 단계별 폼 렌더링
        switch(step) {
            case 1:
                container.innerHTML = this.renderStep1();
                break;
            case 2:
                container.innerHTML = this.renderStep2();
                break;
            case 3:
                container.innerHTML = this.renderStep3();
                break;
            case 4:
                container.innerHTML = this.renderStep4();
                break;
        }
        
        // 이전 단계로 돌아갈 때 저장된 데이터 복원
        this.restoreFormData(step);
        
        this.currentStep = step;
    }
    
    renderStep1() {
        return `
            <div class="step-content">
                <h6 class="mb-3 text-primary">
                    <i class="fas fa-user me-2"></i>기본 정보를 입력해주세요
                </h6>
                
                <div class="row g-3">
                    <div class="col-md-6">
                        <label for="regName" class="form-label">이름 <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" id="regName" name="name" required>
                        <div class="invalid-feedback">이름을 입력해주세요.</div>
                    </div>
                    
                    <div class="col-md-6">
                        <label for="regEmail" class="form-label">이메일 <span class="text-danger">*</span></label>
                        <input type="email" class="form-control" id="regEmail" name="email" required>
                        <div class="invalid-feedback">올바른 이메일을 입력해주세요.</div>
                    </div>
                    
                    <div class="col-md-6">
                        <label for="regPassword" class="form-label">비밀번호 <span class="text-danger">*</span></label>
                        <div class="input-group">
                            <input type="password" class="form-control" id="regPassword" name="password" required>
                            <button class="btn btn-outline-secondary" type="button" onclick="enhancedRegistration.togglePassword('regPassword')">
                                <i class="fas fa-eye"></i>
                            </button>
                        </div>
                        <div class="form-text">6자 이상, 영문, 숫자 포함</div>
                        <div class="invalid-feedback">비밀번호 조건을 만족해주세요.</div>
                    </div>
                    
                    <div class="col-md-6">
                        <label for="regPasswordConfirm" class="form-label">비밀번호 확인 <span class="text-danger">*</span></label>
                        <input type="password" class="form-control" id="regPasswordConfirm" name="password_confirm" required>
                        <div class="invalid-feedback">비밀번호가 일치하지 않습니다.</div>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderStep2() {
        return `
            <div class="step-content">
                <h6 class="mb-3 text-primary">
                    <i class="fas fa-building me-2"></i>추가 정보를 입력해주세요
                </h6>
                
                <div class="row g-3">
                    <div class="col-md-6">
                        <label for="regCompany" class="form-label">회사명</label>
                        <input type="text" class="form-control" id="regCompany" name="company" placeholder="회사명을 입력해주세요">
                        <div class="form-text">선택사항입니다</div>
                    </div>
                    
                    <div class="col-md-6">
                        <label for="regPhone" class="form-label">휴대폰 번호 <span class="text-danger">*</span></label>
                        <input type="tel" class="form-control" id="regPhone" name="phone" placeholder="010-1234-5678" required>
                        <div class="invalid-feedback">올바른 휴대폰 번호를 입력해주세요.</div>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderStep3() {
        return `
            <div class="step-content">
                <h6 class="mb-3 text-primary">
                    <i class="fas fa-cogs me-2"></i>서비스 설정을 선택해주세요
                </h6>
                
                <div class="row g-3">
                    <div class="col-12">
                        <label class="form-label">사용 목적</label>
                        <div class="row g-2">
                            <div class="col-md-6">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="purpose1" name="purpose" value="monitoring">
                                    <label class="form-check-label" for="purpose1">
                                        <i class="fas fa-eye text-primary me-2"></i>24시간 모니터링
                                    </label>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="purpose2" name="purpose" value="prevention">
                                    <label class="form-check-label" for="purpose2">
                                        <i class="fas fa-shield-alt text-success me-2"></i>사전 예방
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderStep4() {
        return `
            <div class="step-content">
                <h6 class="mb-3 text-primary">
                    <i class="fas fa-check-circle me-2"></i>약관 동의 및 회원가입 완료
                </h6>
                
                <div class="row g-3">
                    <div class="col-12">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="privacyAgree" name="privacy_agree" required>
                            <label class="form-check-label" for="privacyAgree">
                                <a href="#" class="text-primary">개인정보처리방침</a>에 동의합니다 <span class="text-danger">*</span>
                            </label>
                        </div>
                    </div>
                    
                    <div class="col-12">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="termsAgree" name="terms_agree" required>
                            <label class="form-check-label" for="termsAgree">
                                <a href="#" class="text-primary">서비스 이용약관</a>에 동의합니다 <span class="text-danger">*</span>
                            </label>
                        </div>
                    </div>
                    
                    <div class="col-12">
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            회원가입 완료 후 관리자 대시보드에서 추가 설정을 할 수 있습니다.
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    nextStep() {
        if (this.validateCurrentStep()) {
            // 각 단계에서는 데이터를 임시 저장만 (API 호출 안함)
            this.collectStepData();
            console.log(`단계 ${this.currentStep} 완료, 저장된 데이터:`, this.formData);
            if (this.currentStep < this.totalSteps) {
                this.renderStep(this.currentStep + 1);
            }
        }
    }
    
    previousStep() {
        if (this.currentStep > 1) {
            // 현재 단계의 데이터를 먼저 저장
            this.collectStepData();
            this.renderStep(this.currentStep - 1);
        }
    }
    
    validateCurrentStep() {
        const currentStepForm = document.querySelector('#registrationFormContainer .step-content');
        const requiredFields = currentStepForm.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });
        
        // 특별 검증
        if (this.currentStep === 1) {
            const password = document.getElementById('regPassword').value;
            const passwordConfirm = document.getElementById('regPasswordConfirm').value;
            
            if (password !== passwordConfirm) {
                document.getElementById('regPasswordConfirm').classList.add('is-invalid');
                isValid = false;
            }
        }
        
        return isValid;
    }
    
    validateField(field) {
        const value = field.value.trim();
        let isValid = true;
        
        // 필수 필드 검증
        if (field.hasAttribute('required') && !value) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
        
        // 이메일 검증
        if (field.type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                field.classList.add('is-invalid');
                isValid = false;
            }
        }
        
        // 비밀번호 검증 (더 유연한 조건)
        if (field.name === 'password' && value) {
            // 최소 6자 이상, 영문과 숫자 포함 (특수문자는 선택사항)
            const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{6,}$/;
            if (!passwordRegex.test(value)) {
                field.classList.add('is-invalid');
                isValid = false;
            }
        }
        
        // 전화번호 검증
        if (field.type === 'tel' && value) {
            const phoneRegex = /^010-\d{4}-\d{4}$/;
            if (!phoneRegex.test(value)) {
                field.classList.add('is-invalid');
                isValid = false;
            }
        }
        
        // 핸드폰 번호 필수 검증
        if (field.name === 'phone' && field.hasAttribute('required') && !value) {
            field.classList.add('is-invalid');
            isValid = false;
        }
        
        return isValid;
    }
    
    restoreFormData(step) {
        // 저장된 데이터를 현재 단계의 폼에 복원
        const currentStepForm = document.querySelector('#registrationFormContainer .step-content');
        if (!currentStepForm) return;
        
        const inputs = currentStepForm.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            if (input.type === 'checkbox') {
                // 체크박스의 경우 배열에서 확인
                if (this.formData[input.name] && Array.isArray(this.formData[input.name])) {
                    input.checked = this.formData[input.name].includes(input.value);
                }
            } else {
                // 일반 입력 필드의 경우 값 복원
                if (this.formData[input.name]) {
                    input.value = this.formData[input.name];
                }
            }
        });
        
        console.log(`단계 ${step} 데이터 복원 완료:`, this.formData);
    }
    
    collectStepData() {
        const currentStepForm = document.querySelector('#registrationFormContainer .step-content');
        const inputs = currentStepForm.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            if (input.type === 'checkbox') {
                if (input.checked) {
                    if (!this.formData[input.name]) {
                        this.formData[input.name] = [];
                    }
                    // 중복 방지
                    if (!this.formData[input.name].includes(input.value)) {
                        this.formData[input.name].push(input.value);
                    }
                } else {
                    // 체크 해제된 경우 배열에서 제거
                    if (this.formData[input.name] && Array.isArray(this.formData[input.name])) {
                        this.formData[input.name] = this.formData[input.name].filter(value => value !== input.value);
                    }
                }
            } else {
                // 기존 데이터를 덮어쓰지 않고 병합
                if (input.value.trim() !== '') {
                    this.formData[input.name] = input.value;
                }
            }
        });
        
        console.log(`단계 ${this.currentStep} 데이터 수집:`, this.formData);
        
        // 데이터가 제대로 저장되었는지 확인
        if (Object.keys(this.formData).length === 0) {
            console.warn('데이터가 저장되지 않았습니다!');
        }
    }
    
    collectAllStepData() {
        // 현재 단계의 데이터를 먼저 수집
        this.collectStepData();
        
        console.log('최종 데이터 수집 전 기존 데이터:', this.formData);
        
        // 현재 폼에서 직접 데이터 수집 (안전장치)
        const currentStepForm = document.querySelector('#registrationFormContainer .step-content');
        if (currentStepForm) {
            const inputs = currentStepForm.querySelectorAll('input, select, textarea');
            
            inputs.forEach(input => {
                if (input.type === 'checkbox') {
                    if (input.checked) {
                        if (!this.formData[input.name]) {
                            this.formData[input.name] = [];
                        }
                        if (!this.formData[input.name].includes(input.value)) {
                            this.formData[input.name].push(input.value);
                        }
                    }
                } else {
                    if (input.value.trim() !== '') {
                        this.formData[input.name] = input.value;
                    }
                }
            });
        }
        
        // API에서 요구하는 필드명으로 변환
        this.formData = {
            ...this.formData,
            username: this.formData.name || this.formData.username, // API에서 요구하는 필드명
            full_name: this.formData.name || this.formData.username, // API에서 요구하는 필드명
            role: 'user', // 기본 역할
            // 필수 동의 항목들 (기본값 설정)
            privacy_agree: this.formData.privacy_agree || false,
            terms_agree: this.formData.terms_agree || false,
            marketing_agree: this.formData.marketing_agree || false
        };
        
        console.log('최종 수집된 회원가입 데이터:', this.formData);
    }
    
    async submitRegistration() {
        if (!this.validateCurrentStep()) {
            return;
        }
        
        // 4단계 모두 완료 후 최종 제출 시에만 데이터 수집
        this.collectAllStepData();
        
        // 필수 필드 검증
        const requiredFields = ['username', 'email', 'password'];
        const missingFields = requiredFields.filter(field => !this.formData[field]);
        
        if (missingFields.length > 0) {
            console.error('누락된 필수 필드:', missingFields);
            this.showError(`필수 필드가 누락되었습니다: ${missingFields.join(', ')}`);
            return;
        }
        
        // 필수 동의 항목 검증
        if (!this.formData.privacy_agree || !this.formData.terms_agree) {
            this.showError('개인정보처리방침 및 서비스 이용약관에 동의해주세요.');
            return;
        }
        
        console.log('서버로 전송할 최종 데이터:', this.formData);
        
        try {
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(this.formData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccessModal();
            } else {
                console.error('서버 응답 오류:', data);
                this.showError(data.message || '회원가입에 실패했습니다.');
            }
        } catch (error) {
            console.error('회원가입 오류:', error);
            this.showError('회원가입 중 오류가 발생했습니다.');
        }
    }
    
    showSuccessModal() {
        const modal = bootstrap.Modal.getInstance(document.getElementById('enhancedRegisterModal'));
        modal.hide();
        
        // 성공 모달 표시
        const successModal = `
            <div class="modal fade" id="registrationSuccessModal" tabindex="-1">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content border-0 shadow-lg">
                        <div class="modal-body text-center p-5">
                            <div class="mb-4">
                                <i class="fas fa-check-circle text-success" style="font-size: 4rem;"></i>
                            </div>
                            <h3 class="text-success mb-3">회원가입 완료!</h3>
                            <p class="text-muted mb-4">
                                Signalcraft AI 진단 서비스에 오신 것을 환영합니다.<br>
                                첫 달 <strong class="text-primary">50% 할인</strong> 혜택이 적용되었습니다.
                            </p>
                            <div class="d-grid gap-2">
                                <button class="btn btn-primary btn-lg" onclick="location.reload()">
                                    <i class="fas fa-rocket me-2"></i>서비스 시작하기
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', successModal);
        const successModalInstance = new bootstrap.Modal(document.getElementById('registrationSuccessModal'));
        successModalInstance.show();
    }
    
    showError(message) {
        alert('오류: ' + message);
    }
    
    togglePassword(fieldId) {
        const field = document.getElementById(fieldId);
        const button = field.nextElementSibling;
        const icon = button.querySelector('i');
        
        if (field.type === 'password') {
            field.type = 'text';
            icon.className = 'fas fa-eye-slash';
        } else {
            field.type = 'password';
            icon.className = 'fas fa-eye';
        }
    }
    
    searchAddress() {
        // 주소 검색 API 연동 (실제 구현 시)
        alert('주소 검색 기능은 추후 구현 예정입니다.');
    }
}

// 전역 인스턴스 생성
const enhancedRegistration = new EnhancedRegistration();


    

