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

// 모바일 네비게이션 토글 기능
function initMobileMenu() {
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const mobileMenuClose = document.querySelector('.mobile-menu-close');
    const mobileNav = document.querySelector('.mobile-nav');
    
    // 요소가 존재하지 않으면 나중에 다시 시도
    if (!mobileMenuToggle || !mobileMenuClose || !mobileNav) {
        return false; // 초기화 실패
    }
    
    mobileMenuToggle.addEventListener('click', function() {
        mobileNav.classList.add('active');
    });
    
    mobileMenuClose.addEventListener('click', function() {
        mobileNav.classList.remove('active');
    });
    
    // 모바일 메뉴 외부 클릭 시 닫기
    document.addEventListener('click', function(event) {
        if (mobileNav.classList.contains('active') && 
            !mobileNav.contains(event.target) && 
            !mobileMenuToggle.contains(event.target)) {
            mobileNav.classList.remove('active');
        }
    });
    
    // 링크 클릭 시 메뉴 닫기
    const mobileLinks = document.querySelectorAll('.mobile-nav a');
    mobileLinks.forEach(link => {
        link.addEventListener('click', function() {
            mobileNav.classList.remove('active');
        });
    });
    
    return true; // 초기화 성공
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    initSmoothScroll();
    
    // 모바일 메뉴 초기화 시도
    let mobileMenuInitialized = initMobileMenu();
    
    // 만약 초기화 실패 시 주기적으로 다시 시도
    if (!mobileMenuInitialized) {
        const mobileMenuInterval = setInterval(function() {
            mobileMenuInitialized = initMobileMenu();
            if (mobileMenuInitialized) {
                clearInterval(mobileMenuInterval); // 성공 시 인터벌 종료
            }
        }, 100);
        
        // 최대 5초 동안 시도 후 종료
        setTimeout(function() {
            clearInterval(mobileMenuInterval);
        }, 5000);
    }
});