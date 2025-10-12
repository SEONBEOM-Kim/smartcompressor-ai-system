document.addEventListener('DOMContentLoaded', () => {
    const loadComponent = (id, url, callback) => {
        fetch(url)
            .then(response => response.text())
            .then(data => {
                const element = document.getElementById(id);
                if (element) {
                    element.innerHTML = data;
                }
                if (callback) {
                    callback();
                }
            })
            .catch(error => console.error(`Error loading ${url}:`, error));
    };

    loadComponent('header-placeholder', '/static/landing-components/header.html');
    loadComponent('hero-placeholder', '/static/landing-components/hero.html');
    loadComponent('features-placeholder', '/static/landing-components/features.html');
    
    // demo.html 로드 후, 콜백으로 AI 진단 기능 초기화
    loadComponent('demo-placeholder', '/static/landing-components/demo.html', () => {
        new IntegratedAIDiagnosis();
    });

    loadComponent('pricing-placeholder', '/static/landing-components/pricing.html');
    loadComponent('footer-placeholder', '/static/landing-components/footer.html');
});
