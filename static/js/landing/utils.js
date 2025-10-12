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