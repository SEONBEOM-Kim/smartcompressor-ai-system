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
                                <span class="badge bg-light text-dark">2. 회사 정보</span>
                                <span class="badge bg-light text-dark">3. 서비스 설정</span>
                                <span class="badge bg-light text-dark">4. 알림 설정</span>
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
                        <div class="form-text">8자 이상, 영문, 숫자, 특수문자 포함</div>
                        <div class="invalid-feedback">비밀번호 조건을 만족해주세요.</div>
                    </div>
                    
                    <div class="col-md-6">
                        <label for="regPasswordConfirm" class="form-label">비밀번호 확인 <span class="text-danger">*</span></label>
                        <input type="password" class="form-control" id="regPasswordConfirm" name="password_confirm" required>
                        <div class="invalid-feedback">비밀번호가 일치하지 않습니다.</div>
                    </div>
                    
                    <div class="col-md-6">
                        <label for="regPhone" class="form-label">휴대폰 번호 <span class="text-danger">*</span></label>
                        <input type="tel" class="form-control" id="regPhone" name="phone" placeholder="010-1234-5678" required>
                        <div class="invalid-feedback">올바른 휴대폰 번호를 입력해주세요.</div>
                    </div>
                    
                    <div class="col-md-6">
                        <label for="regPosition" class="form-label">직책</label>
                        <select class="form-select" id="regPosition" name="position">
                            <option value="">선택해주세요</option>
                            <option value="ceo">대표이사</option>
                            <option value="manager">매니저</option>
                            <option value="engineer">엔지니어</option>
                            <option value="technician">기술자</option>
                            <option value="other">기타</option>
                        </select>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderStep2() {
        return `
            <div class="step-content">
                <h6 class="mb-3 text-primary">
                    <i class="fas fa-building me-2"></i>회사 정보를 입력해주세요
                </h6>
                
                <div class="row g-3">
                    <div class="col-md-6">
                        <label for="regCompany" class="form-label">회사명 <span class="text-danger">*</span></label>
                        <input type="text" class="form-control" id="regCompany" name="company" required>
                        <div class="invalid-feedback">회사명을 입력해주세요.</div>
                    </div>
                    
                    <div class="col-md-6">
                        <label for="regIndustry" class="form-label">산업군</label>
                        <select class="form-select" id="regIndustry" name="industry">
                            <option value="">선택해주세요</option>
                            <option value="retail">소매업</option>
                            <option value="food">식품업</option>
                            <option value="manufacturing">제조업</option>
                            <option value="logistics">물류업</option>
                            <option value="hospitality">호텔/관광업</option>
                            <option value="healthcare">의료업</option>
                            <option value="education">교육업</option>
                            <option value="other">기타</option>
                        </select>
                    </div>
                    
                    <div class="col-md-6">
                        <label for="regCompanySize" class="form-label">회사 규모</label>
                        <select class="form-select" id="regCompanySize" name="company_size">
                            <option value="">선택해주세요</option>
                            <option value="1-10">1-10명</option>
                            <option value="11-50">11-50명</option>
                            <option value="51-200">51-200명</option>
                            <option value="201-500">201-500명</option>
                            <option value="500+">500명 이상</option>
                        </select>
                    </div>
                    
                    <div class="col-md-6">
                        <label for="regCompanyEmail" class="form-label">회사 이메일</label>
                        <input type="email" class="form-control" id="regCompanyEmail" name="company_email">
                        <div class="form-text">회사 이메일이 있으시면 입력해주세요</div>
                    </div>
                    
                    <div class="col-12">
                        <label for="regAddress" class="form-label">회사 주소</label>
                        <div class="input-group">
                            <input type="text" class="form-control" id="regAddress" name="address" placeholder="서울시 강남구 테헤란로 123">
                            <button class="btn btn-outline-secondary" type="button" onclick="enhancedRegistration.searchAddress()">
                                <i class="fas fa-search me-1"></i>주소 검색
                            </button>
                        </div>
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
                        <label class="form-label">사용 목적 <span class="text-danger">*</span></label>
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
                            <div class="col-md-6">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="purpose3" name="purpose" value="cost_reduction">
                                    <label class="form-check-label" for="purpose3">
                                        <i class="fas fa-chart-line text-warning me-2"></i>비용 절감
                                    </label>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="purpose4" name="purpose" value="efficiency">
                                    <label class="form-check-label" for="purpose4">
                                        <i class="fas fa-tachometer-alt text-info me-2"></i>운영 효율성
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-md-6">
                        <label for="regBudget" class="form-label">월 예산</label>
                        <select class="form-select" id="regBudget" name="budget">
                            <option value="">선택해주세요</option>
                            <option value="under_50k">50만원 미만</option>
                            <option value="50k_100k">50-100만원</option>
                            <option value="100k_200k">100-200만원</option>
                            <option value="200k_500k">200-500만원</option>
                            <option value="500k_plus">500만원 이상</option>
                        </select>
                    </div>
                    
                    <div class="col-md-6">
                        <label for="regTimeline" class="form-label">도입 시기</label>
                        <select class="form-select" id="regTimeline" name="timeline">
                            <option value="">선택해주세요</option>
                            <option value="immediate">즉시</option>
                            <option value="1_month">1개월 내</option>
                            <option value="3_months">3개월 내</option>
                            <option value="6_months">6개월 내</option>
                            <option value="1_year">1년 내</option>
                        </select>
                    </div>
                    
                    <div class="col-12">
                        <label for="regDevices" class="form-label">예상 디바이스 수</label>
                        <select class="form-select" id="regDevices" name="device_count">
                            <option value="">선택해주세요</option>
                            <option value="1">1개</option>
                            <option value="2-5">2-5개</option>
                            <option value="6-10">6-10개</option>
                            <option value="11-20">11-20개</option>
                            <option value="20_plus">20개 이상</option>
                        </select>
                    </div>
                </div>
            </div>
        `;
    }
    
    renderStep4() {
        return `
            <div class="step-content">
                <h6 class="mb-3 text-primary">
                    <i class="fas fa-bell me-2"></i>알림 설정을 선택해주세요
                </h6>
                
                <div class="row g-3">
                    <div class="col-12">
                        <div class="card border-0 bg-light">
                            <div class="card-body">
                                <h6 class="card-title">
                                    <i class="fas fa-envelope text-primary me-2"></i>이메일 알림
                                </h6>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="emailAlerts" name="email_alerts" checked>
                                    <label class="form-check-label" for="emailAlerts">
                                        이상 감지 시 이메일로 알림 받기
                                    </label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="emailNewsletter" name="email_newsletter">
                                    <label class="form-check-label" for="emailNewsletter">
                                        서비스 업데이트 및 뉴스레터 수신
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="col-12">
                        <div class="card border-0 bg-light">
                            <div class="card-body">
                                <h6 class="card-title">
                                    <i class="fas fa-mobile-alt text-success me-2"></i>SMS/카카오톡 알림
                                </h6>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="smsAlerts" name="sms_alerts" checked>
                                    <label class="form-check-label" for="smsAlerts">
                                        긴급 상황 시 SMS/카카오톡으로 알림 받기
                                    </label>
                                </div>
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="kakaoAlerts" name="kakao_alerts">
                                    <label class="form-check-label" for="kakaoAlerts">
                                        카카오톡으로 상세 알림 받기
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                    
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
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="marketingAgree" name="marketing_agree">
                            <label class="form-check-label" for="marketingAgree">
                                마케팅 정보 수신에 동의합니다 (선택)
                            </label>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    nextStep() {
        if (this.validateCurrentStep()) {
            this.collectStepData();
            if (this.currentStep < this.totalSteps) {
                this.renderStep(this.currentStep + 1);
            }
        }
    }
    
    previousStep() {
        if (this.currentStep > 1) {
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
        
        // 비밀번호 검증
        if (field.name === 'password' && value) {
            const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;
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
        
        return isValid;
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
                    this.formData[input.name].push(input.value);
                }
            } else {
                this.formData[input.name] = input.value;
            }
        });
    }
    
    async submitRegistration() {
        if (!this.validateCurrentStep()) {
            return;
        }
        
        this.collectStepData();
        
        try {
            const response = await fetch('/api/auth/register-enhanced', {
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
