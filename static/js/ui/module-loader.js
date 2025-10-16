// Ensure components are loaded only after all managers are ready
function loadComponentsWhenReady() {
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
    
    // Load detailed feature components after main features section loads
    setTimeout(() => {
        loadComponent('feature-detailed-ai-analysis', '/static/landing-components/features/ai-analysis.html');
        loadComponent('feature-detailed-monitoring', '/static/landing-components/features/monitoring.html');
        loadComponent('feature-detailed-notifications', '/static/landing-components/features/notifications.html');
        loadComponent('feature-detailed-mobile-access', '/static/landing-components/features/mobile-access.html');
        loadComponent('feature-detailed-integrations', '/static/landing-components/features/integrations.html');
    }, 100); // Small delay to ensure parent container is available
}

document.addEventListener('DOMContentLoaded', () => {
    // Check if managers are ready, otherwise wait for them
    if (typeof authManager !== 'undefined' && 
        typeof modalManager !== 'undefined' && 
        typeof navbarRenderer !== 'undefined' && 
        typeof kakaoOAuth !== 'undefined') {
        // Managers are already available, load components immediately
        loadComponentsWhenReady();
    } else {
        // Managers aren't available yet, wait and check periodically
        const checkManagersInterval = setInterval(() => {
            if (typeof authManager !== 'undefined' && 
                typeof modalManager !== 'undefined' && 
                typeof navbarRenderer !== 'undefined' && 
                typeof kakaoOAuth !== 'undefined') {
                
                clearInterval(checkManagersInterval);
                loadComponentsWhenReady();
            }
        }, 50); // Check every 50ms
        
        // Clear the interval after 5 seconds to prevent infinite loop
        setTimeout(() => {
            clearInterval(checkManagersInterval);
        }, 5000);
    }
});
