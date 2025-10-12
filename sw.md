# Answer

랜딩 페이지 모듈화를 완료했다면, 다음 단계는 **`static/app.js` 모듈화**를 추천합니다. 이 파일은 800줄 이상의 코드를 포함하고 있으며[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/app.js:0-833], 모든 페이지에서 공통으로 사용되는 핵심 기능을 담당하고 있습니다.<cite />

## Phase 2: app.js 모듈화 (우선순위 2)

### 현재 app.js의 구조

`static/app.js`는 다음 기능들을 포함합니다:
- 인증 관리 (로그인/로그아웃)[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/app.js:30-54]
- Kakao OAuth 통합[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/app.js:355-477]
- UI 상태 관리 (네비게이션 렌더링)[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/app.js:56-150]
- 모달 시스템[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/app.js:520-640]
- 전역 함수 등록[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/app.js:757-760]

### 2.1 폴더 구조 생성

```
static/js/
  ├── auth/
  │   ├── auth-manager.js (새로 생성)
  │   ├── kakao-oauth.js (새로 생성)
  │   └── session-validator.js (새로 생성)
  ├── ui/
  │   ├── navbar-renderer.js (새로 생성)
  │   ├── modal-manager.js (새로 생성)
  │   └── personalized-content.js (새로 생성)
  └── app.js (진입점만 유지)
```

### 2.2 인증 모듈 분리

**`static/js/auth/auth-manager.js` 생성:**

```javascript
// static/js/auth/auth-manager.js
class AuthManager {
    constructor() {
        this.currentUser = null;
        this.authToken = null;
    }

    async updateLoginStatus() {
        // static/app.js:30-54의 로직 이동
        const token = localStorage.getItem('authToken');
        if (!token) {
            this.showLoggedOutUI();
            return;
        }
        // ... 나머지 로직
    }

    async handleLogin(username, password) {
        // static/app.js:643-693의 로직 이동
    }

    async logout() {
        // static/app.js:695-750의 로직 이동
    }
}
```

**`static/js/auth/kakao-oauth.js` 생성:**

```javascript
// static/js/auth/kakao-oauth.js
class KakaoOAuth {
    kakaoLogin() {
        // static/app.js:356-383의 로직 이동
    }

    handleKakaoCallback() {
        // static/app.js:386-405의 로직 이동
    }
}
```

### 2.3 UI 모듈 분리

**`static/js/ui/navbar-renderer.js` 생성:**

```javascript
// static/js/ui/navbar-renderer.js
class NavbarRenderer {
    showLoggedInUI(user) {
        // static/app.js:57-150의 로직 이동
    }

    showLoggedOutUI() {
        // static/app.js:280-353의 로직 이동
    }
}
```

**`static/js/ui/modal-manager.js` 생성:**

```javascript
// static/js/ui/modal-manager.js
class ModalManager {
    showLoginModal() {
        // static/app.js:521-570의 로직 이동
    }

    showRegisterModal() {
        // static/app.js:572-640의 로직 이동
    }
}
```

### 2.4 새로운 app.js 구조

```javascript
// static/app.js (진입점만 유지)
const API_BASE_URL = window.location.origin;

// 전역 인스턴스
let authManager;
let navbarRenderer;
let modalManager;
let kakaoOAuth;

document.addEventListener('DOMContentLoaded', function() {
    console.log('Signalcraft 애플리케이션이 초기화되었습니다.');
    
    // 인스턴스 생성
    authManager = new AuthManager();
    navbarRenderer = new NavbarRenderer();
    modalManager = new ModalManager();
    kakaoOAuth = new KakaoOAuth();
    
    // 초기화
    setupEventListeners();
    checkLoginSuccess();
    kakaoOAuth.handleKakaoCallback();
    authManager.updateLoginStatus();
});

// 전역 함수로 등록 (기존 호환성 유지)
window.showLoginModal = () => modalManager.showLoginModal();
window.showRegisterModal = () => modalManager.showRegisterModal();
window.updateLoginStatus = () => authManager.updateLoginStatus();
window.kakaoLogin = () => kakaoOAuth.kakaoLogin();
```

### 2.5 HTML 파일 업데이트

모든 HTML 파일에서 스크립트 로드 순서 변경:

```html
<!-- 기존 -->
<script src="/static/app.js"></script>

<!-- 모듈화 후 -->
<script src="/static/js/auth/auth-manager.js"></script>
<script src="/static/js/auth/kakao-oauth.js"></script>
<script src="/static/js/ui/navbar-renderer.js"></script>
<script src="/static/js/ui/modal-manager.js"></script>
<script src="/static/app.js"></script>
```

## 실행 단계

### Step 1: 인증 모듈 분리 (2-3일)
1. `static/js/auth/` 폴더 생성
2. `auth-manager.js`, `kakao-oauth.js` 파일 생성
3. 로그인/로그아웃 로직 이동
4. 테스트: 로그인, 로그아웃, Kakao OAuth 정상 작동 확인

### Step 2: UI 모듈 분리 (2-3일)
1. `static/js/ui/` 폴더 생성
2. `navbar-renderer.js`, `modal-manager.js` 파일 생성
3. UI 렌더링 로직 이동
4. 테스트: 네비게이션 바, 모달 정상 작동 확인

### Step 3: app.js 간소화 (1일)
1. 진입점 로직만 남기고 나머지 제거
2. 전역 함수 등록 유지 (기존 호환성)
3. 전체 페이지 테스트

### Step 4: 다른 페이지 업데이트 (1-2일)
1. `templates/dashboard.html`[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: templates/dashboard.html:581-584]
2. `templates/mobile_app.html`[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: templates/mobile_app.html:414-417]
3. 모든 HTML 파일에서 스크립트 로드 순서 업데이트

## 체크리스트

- [ ] `static/js/auth/auth-manager.js` 생성 및 테스트
- [ ] `static/js/auth/kakao-oauth.js` 생성 및 테스트
- [ ] `static/js/ui/navbar-renderer.js` 생성 및 테스트
- [ ] `static/js/ui/modal-manager.js` 생성 및 테스트
- [ ] `app.js` 간소화 (800줄 → 100줄 목표)
- [ ] 모든 페이지에서 인증 기능 정상 작동 확인
- [ ] 배포 파이프라인 테스트

## 주의사항

1. **전역 함수 호환성 유지**: 기존 HTML에서 `onclick="showLoginModal()"` 같은 인라인 이벤트 핸들러가 있으므로 전역 함수 등록 필수[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/app.js:757-760]
2. **의존성 순서**: 모듈 파일들을 `app.js`보다 먼저 로드해야 함
3. **localStorage 접근**: 모든 모듈에서 `localStorage`를 사용하므로 브라우저 호환성 확인

# Notes

`app.js` 모듈화가 완료되면, 다음 단계는 `static/js/dashboard.js` (800줄 이상)[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/js/dashboard.js:1-847], `static/js/mobile_app.js`[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/js/mobile_app.js:1-675], `static/js/notification_dashboard.js`[link to Repo SEONBEOM-Kim/smartcompressor-ai-system: static/js/notification_dashboard.js:1-552] 순서로 진행하는 것을 권장합니다. 각 파일은 독립적인 페이지에서 사용되므로 병렬로 작업 가능합니다.

Wiki pages you might want to explore:
- [Frontend Applications (SEONBEOM-Kim/smartcompressor-ai-system)](/wiki/SEONBEOM-Kim/smartcompressor-ai-system#3)

Wiki pages you might want to explore:
- [Overview (SEONBEOM-Kim/smartcompressor-ai-system)](/wiki/SEONBEOM-Kim/smartcompressor-ai-system#1)