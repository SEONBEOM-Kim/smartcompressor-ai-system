// Google Analytics 커스텀 이벤트 트래킹
class GAAnalytics {
    static trackEvent(eventName, parameters = {}) {
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, parameters);
        }
    }
    
    static trackPageView(pageName) {
        if (typeof gtag !== 'undefined') {
            gtag('event', 'page_view', {
                page_title: pageName,
                page_location: window.location.href
            });
        }
    }
}

// 페이지 로드 시 기본 트래킹
document.addEventListener('DOMContentLoaded', function() {
    // 페이지 뷰 트래킹
    GAAnalytics.trackPageView(document.title);
    
    // AI 진단 관련 이벤트 트래킹
    const startBtn = document.getElementById('start-recording');
    if (startBtn) {
        startBtn.addEventListener('click', function() {
            GAAnalytics.trackEvent('ai_diagnosis_started', {
                event_category: 'AI 진단',
                event_label: '녹음 시작'
            });
        });
    }
    
    const stopBtn = document.getElementById('stop-recording');
    if (stopBtn) {
        stopBtn.addEventListener('click', function() {
            GAAnalytics.trackEvent('ai_diagnosis_completed', {
                event_category: 'AI 진단',
                event_label: '녹음 완료'
            });
        });
    }
    
    const analyzeBtn = document.getElementById('analyze-audio');
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', function() {
            GAAnalytics.trackEvent('ai_analysis_started', {
                event_category: 'AI 진단',
                event_label: '분석 시작'
            });
        });
    }
    
    // 상세 리포트 보기 버튼 트래킹
    const reportBtn = document.getElementById('view-report');
    if (reportBtn) {
        reportBtn.addEventListener('click', function() {
            GAAnalytics.trackEvent('report_viewed', {
                event_category: '사용자 행동',
                event_label: '상세 리포트 보기'
            });
        });
    }
    
    // 가격 문의 버튼 트래킹
    const contactBtns = document.querySelectorAll('.contact-btn, .pricing-btn');
    contactBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            GAAnalytics.trackEvent('contact_clicked', {
                event_category: '사용자 행동',
                event_label: '가격 문의'
            });
        });
    });
});
