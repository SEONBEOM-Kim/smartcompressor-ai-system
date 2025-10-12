Answer
랜딩 페이지(static/index.html)를 가장 먼저 모듈화하는 구체적인 플랜을 제시하겠습니다.

현재 랜딩 페이지의 문제점
static/index.html은 약 1,300줄의 코드로 구성되어 있으며, 특히 다음 부분들이 모듈화가 필요합니다:

인라인 JavaScript (약 200줄): IntegratedAIDiagnosis 클래스 index.html:1104-1286
인라인 CSS (약 500줄): 스타일 정의 index.html:9-537
유틸리티 함수: 스크롤 및 플랜 선택 함수 index.html:1075-1100
Phase 1: 인라인 JavaScript 분리 (우선순위 1)
1.1 AI 진단 클래스 분리
새 파일 생성: static/js/landing/ai-diagnosis.js

// static/js/landing/ai-diagnosis.js  
class IntegratedAIDiagnosis {  
    constructor() {  
        this.isRecording = false;  
        this.mediaRecorder = null;  
        this.audioChunks = [];  
        this.audioBlob = null;  
        this.diagnosisResult = null;  
        this.init();  
    }  
      
    // 기존 메서드들을 그대로 이동  
    init() { /* ... */ }  
    checkBrowserSupport() { /* ... */ }  
    toggleRecording() { /* ... */ }  
    analyzeAudio() { /* ... */ }  
    // ... 나머지 메서드들  
}  
  
// 페이지 로드 시 자동 초기화  
document.addEventListener('DOMContentLoaded', () => {  
    new IntegratedAIDiagnosis();  
});
static/index.html 수정:

<!-- 기존 인라인 스크립트 제거 -->  
<script src="/static/js/landing/ai-diagnosis.js"></script>
1.2 유틸리티 함수 분리
새 파일 생성: static/js/landing/utils.js

// static/js/landing/utils.js  
  
// 부드러운 스크롤  
function scrollToSection(sectionId) {  
    document.getElementById(sectionId).scrollIntoView({  
        behavior: 'smooth'  
    });  
}  
  
// 요금제 선택  
function selectPlan(planType) {  
    console.log('선택된 플랜:', planType);  
    showRegisterModal();  
}  
  
// 네비게이션 링크 초기화  
function initSmoothScroll() {  
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {  
        anchor.addEventListener('click', function (e) {  
            e.preventDefault();  
            const target = document.querySelector(this.getAttribute('href'));  
            if (target) {  
                target.scrollIntoView({ behavior: 'smooth' });  
            }  
        });  
    });  
}  
  
// 페이지 로드 시 초기화  
document.addEventListener('DOMContentLoaded', initSmoothScroll);
Phase 2: 인라인 CSS 분리 (우선순위 2)
2.1 CSS 파일 생성
새 파일 생성: static/css/landing.css

현재 <style> 태그 내의 모든 CSS를 이동 index.html:9-537 :

/* static/css/landing.css */  
  
/* Hero Section */  
.hero-section {  
    background: linear-gradient(135deg, #000000 0%, #111111 50%, #1a1a1a 100%);  
    color: #ffffff;  
    padding: 150px 0;  
    min-height: 100vh;  
    display: flex;  
    align-items: center;  
}  
  
/* Feature Cards */  
.feature-card {  
    transition: transform 0.3s ease;  
    border: none;  
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);  
    margin-bottom: 3rem;  
    padding: 3rem 2rem;  
}  
  
/* ... 나머지 스타일들 */
static/index.html 수정:

<head>  
    <!-- 기존 인라인 스타일 제거 -->  
    <link rel="stylesheet" href="/static/css/landing.css">  
</head>
Phase 3: HTML 구조 정리 (우선순위 3)
3.1 섹션별 파일 분리 (선택사항)
더 나아가 HTML도 모듈화하려면 템플릿 시스템 활용:

새 파일 생성: templates/landing/

templates/landing/  
  ├── hero.html  
  ├── features.html  
  ├── demo.html  
  └── footer.html  
Flask에서 include 사용:

<!-- templates/landing.html -->  
{% include 'landing/hero.html' %}  
{% include 'landing/features.html' %}  
{% include 'landing/demo.html' %}  
{% include 'landing/footer.html' %}
최종 폴더 구조
static/  
  ├── css/  
  │   └── landing.css (새로 생성)  
  ├── js/  
  │   ├── landing/  
  │   │   ├── ai-diagnosis.js (새로 생성)  
  │   │   └── utils.js (새로 생성)  
  │   ├── app.js (기존 유지)  
  │   ├── notification-manager.js (기존 유지)  
  │   └── enhanced-registration.js (기존 유지)  
  └── index.html (간소화됨)  
실행 단계
Step 1: AI 진단 클래스 분리 (1-2일)
static/js/landing/ 폴더 생성
ai-diagnosis.js 파일 생성 및 코드 이동
index.html에서 인라인 스크립트 제거 및 외부 스크립트 링크 추가
테스트: 녹음 및 진단 기능 정상 작동 확인
Step 2: 유틸리티 함수 분리 (1일)
utils.js 파일 생성
스크롤 및 플랜 선택 함수 이동
index.html에서 인라인 스크립트 제거
테스트: 네비게이션 스크롤 정상 작동 확인
Step 3: CSS 분리 (1일)
static/css/landing.css 파일 생성
모든 인라인 스타일 이동
index.html에서 <style> 태그 제거 및 외부 CSS 링크 추가
테스트: 모든 스타일 정상 적용 확인
Step 4: 최종 검증 (1일)
전체 페이지 기능 테스트
브라우저 호환성 확인
성능 측정 (로딩 속도)
Git commit 및 배포
체크리스트
 static/js/landing/ai-diagnosis.js 생성 및 테스트
 static/js/landing/utils.js 생성 및 테스트
 static/css/landing.css 생성 및 테스트
 index.html 간소화 (약 600줄 → 300줄 목표)
 모든 기능 정상 작동 확인
 배포 파이프라인 테스트
주의사항
기존 의존성 유지: app.js, notification-manager.js, enhanced-registration.js는 그대로 유지 index.html:1069-1073
전역 함수 호환성: showRegisterModal(), kakaoLogin() 등 전역 함수는 app.js에서 제공되므로 접근 가능
빌드 프로세스 불필요: ES6 모듈 대신 전통적인 스크립트 태그 사용으로 빌드 단계 없이 즉시 적용 가능
Notes
이 플랜은 빌드 프로세스 추가 없이 즉시 적용 가능하며, 기존 배포 파이프라인에 영향을 주지 않습니다. 모듈화 후 index.html은 약 50% 이상 코드가 줄어들어 유지보수가 훨씬 쉬워집니다. 다른 페이지(dashboard.html, mobile_app.html)는 영향받지 않으므로 안전하게 진행할 수 있습니다.