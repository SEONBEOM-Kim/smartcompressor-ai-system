// Mobile-friendly dashboard JavaScript

// Function to load the correct content based on the current page/section
function loadContent(section = 'dashboard') {
    const mainContentElement = document.getElementById('main-content-component');
    const dynamicContentArea = document.getElementById('dynamic-content-area');
    
    if (!mainContentElement) {
        console.error('Main content element not found');
        return;
    }
    
    let contentPath = '';
    
    switch(section) {
        case 'dashboard':
            contentPath = '/static/mobile-friendly-dashboard/main/main-content.html';
            
            // For dashboard, show both main content and the additional components
            fetch('/static/mobile-friendly-dashboard/main/summary-cards.html')
                .then(response => response.text())
                .then(summaryCardsData => {
                    document.getElementById('summary-cards-component').innerHTML = summaryCardsData;
                    
                    fetch('/static/mobile-friendly-dashboard/main/charts-section.html')
                        .then(response => response.text())
                        .then(chartsData => {
                            document.getElementById('charts-section-component').innerHTML = chartsData;
                            
                            // Show the dynamic content area for dashboard
                            dynamicContentArea.style.display = 'block';
                        })
                        .catch(error => console.error('Error loading charts section:', error));
                })
                .catch(error => console.error('Error loading summary cards:', error));
            break;
        case 'anomalies':
            contentPath = '/static/mobile-friendly-dashboard/anomalies/main-content.html';
            break;
        case 'assets':
            contentPath = '/static/mobile-friendly-dashboard/assets/main-content.html';
            break;
        case 'reports':
            contentPath = '/static/mobile-friendly-dashboard/reports/main-content.html';
            break;
        case 'settings':
            contentPath = '/static/mobile-friendly-dashboard/settings/main-content.html';
            break;
        default:
            contentPath = '/static/mobile-friendly-dashboard/main/main-content.html';
    }
    
    fetch(contentPath)
        .then(response => response.text())
        .then(data => {
            mainContentElement.innerHTML = data;
            
            // For non-dashboard sections, hide the summary cards and charts section
            if (section !== 'dashboard') {
                dynamicContentArea.style.display = 'none';
            } else {
                dynamicContentArea.style.display = 'block';
            }
            
            // After loading content, initialize any charts that may exist in the new content
            setTimeout(() => {
                initializeCharts();
            }, 100);
        })
        .catch(error => console.error(`Error loading ${section} content:`, error));
}

document.addEventListener('DOMContentLoaded', function() {
    // Load the default dashboard content
    loadContent('dashboard');
    
    // Initialize charts for the main dashboard
    initializeCharts();
    
    // Handle sidebar toggle on mobile
    const sidebarToggle = document.querySelector('.navbar-toggler');
    const sidebar = document.getElementById('sidebarNav');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            // For mobile, we'll use a different approach to show/hide the sidebar
            if (window.innerWidth < 992) {
                sidebar.classList.toggle('show');
            }
        });
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(event) {
            const isClickInsideSidebar = sidebar.contains(event.target);
            const isClickOnToggler = sidebarToggle.contains(event.target);
            
            if (!isClickInsideSidebar && !isClickOnToggler && window.innerWidth < 992) {
                sidebar.classList.remove('show');
            }
        });
    }
    
    // Add event listeners to sidebar navigation links
    const navLinks = document.querySelectorAll('.sidebar-link');
    if (navLinks) {
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Remove active class from all links
                navLinks.forEach(l => l.classList.remove('active'));
                
                // Add active class to clicked link
                this.classList.add('active');
                
                // Determine which section to load based on the href or text
                let section = this.getAttribute('href').replace('#', '') || 
                             this.querySelector('span').textContent.trim();
                
                // Map Korean text to section names
                switch(section) {
                    case '대시보드':
                        section = 'dashboard';
                        break;
                    case '이상 징후':
                        section = 'anomalies';
                        break;
                    case '자산 목록':
                        section = 'assets';
                        break;
                    case '리포트':
                        section = 'reports';
                        break;
                    case '설정':
                        section = 'settings';
                        break;
                }
                
                // Update the URL hash
                window.location.hash = section;
                
                // Update the content based on the selected section
                loadContent(section);
                
                // On mobile, hide the sidebar after selection
                if (window.innerWidth < 992) {
                    sidebar.classList.remove('show');
                }
            });
        });
    }
    
    // Handle browser back/forward buttons
    window.addEventListener('hashchange', function() {
        const hash = window.location.hash.substring(1) || 'dashboard';
        loadContent(hash);
        
        // Update active link in sidebar
        navLinks.forEach(link => {
            link.classList.remove('active');
            const linkText = link.querySelector('span').textContent.trim();
            let linkSection = linkText;
            
            // Map Korean text to section names
            switch(linkText) {
                case '대시보드':
                    linkSection = 'dashboard';
                    break;
                case '이상 징후':
                    linkSection = 'anomalies';
                    break;
                case '자산 목록':
                    linkSection = 'assets';
                    break;
                case '리포트':
                    linkSection = 'reports';
                    break;
                case '설정':
                    linkSection = 'settings';
                    break;
            }
            
            if (linkSection === hash) {
                link.classList.add('active');
            }
        });
    });
    
    // Initialize based on current hash or default to dashboard
    const initialHash = window.location.hash.substring(1) || 'dashboard';
    loadContent(initialHash);
    
    // Update active link in sidebar for initial load
    navLinks.forEach(link => {
        link.classList.remove('active');
        const linkText = link.querySelector('span').textContent.trim();
        let linkSection = linkText;
        
        // Map Korean text to section names
        switch(linkText) {
            case '대시보드':
                linkSection = 'dashboard';
                break;
            case '이상 징후':
                linkSection = 'anomalies';
                break;
            case '자산 목록':
                linkSection = 'assets';
                break;
            case '리포트':
                linkSection = 'reports';
                break;
            case '설정':
                linkSection = 'settings';
                break;
        }
        
        if (linkSection === initialHash) {
            link.classList.add('active');
        }
    });
    
    // Ensure sidebar closes when clicking outside on mobile
    document.addEventListener('click', function(event) {
        const isClickInsideSidebar = sidebar && sidebar.contains(event.target);
        const isClickOnToggler = sidebarToggle && sidebarToggle.contains(event.target);
        
        if (!isClickInsideSidebar && !isClickOnToggler && window.innerWidth < 992) {
            // Add a small delay to allow for link clicks to register
            setTimeout(() => {
                if (sidebar) {
                    sidebar.classList.remove('show');
                }
            }, 100);
        }
    });
    
    // Close sidebar when a nav link is clicked on mobile
    if (navLinks) {
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                if (window.innerWidth < 992) {
                    setTimeout(() => {
                        if (sidebar) {
                            sidebar.classList.remove('show');
                        }
                    }, 150); // Small delay to allow the navigation to process
                }
            });
        });
    }
});

function initializeCharts() {
    // Asset Status Chart (Doughnut) - only initialize if the element exists
    const assetStatusCtx = document.getElementById('assetStatusChart');
    if (assetStatusCtx && assetStatusCtx.getContext) {
        // Destroy existing chart instance if it exists
        if (assetStatusCtx.chart) {
            assetStatusCtx.chart.destroy();
        }
        
        assetStatusCtx.chart = new Chart(assetStatusCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [85, 15],
                    backgroundColor: [
                        'rgba(72, 187, 120, 0.7)',
                        'rgba(229, 62, 62, 0.7)'
                    ],
                    borderWidth: 0
                }],
                labels: ['정상', '이상']
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                }
            }
        });
    }

    // Threat Summary Chart (Line)
    const threatSummaryCtx = document.getElementById('threatSummaryChart');
    if (threatSummaryCtx && threatSummaryCtx.getContext) {
        // Destroy existing chart instance if it exists
        if (threatSummaryCtx.chart) {
            threatSummaryCtx.chart.destroy();
        }
        
        threatSummaryCtx.chart = new Chart(threatSummaryCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: ['1월', '2월', '3월', '4월', '5월', '6월'],
                datasets: [{
                    label: '이상 징후 수',
                    data: [12, 19, 3, 5, 2, 3],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.1)',
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Threat Type Chart (Doughnut)
    const threatTypeCtx = document.getElementById('threatTypeChart');
    if (threatTypeCtx && threatTypeCtx.getContext) {
        // Destroy existing chart instance if it exists
        if (threatTypeCtx.chart) {
            threatTypeCtx.chart.destroy();
        }
        
        threatTypeCtx.chart = new Chart(threatTypeCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [50, 30, 20],
                    backgroundColor: [
                        'rgba(220, 53, 69, 0.7)',    // danger color
                        'rgba(255, 193, 7, 0.7)',     // warning color
                        'rgba(160, 174, 192, 0.7)'    // info color
                    ],
                    borderWidth: 0
                }],
                labels: ['위험', '경고', '기타']
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                }
            }
        });
    }

    // Asset Threat Chart (Bar)
    const assetThreatCtx = document.getElementById('assetThreatChart');
    if (assetThreatCtx && assetThreatCtx.getContext) {
        // Destroy existing chart instance if it exists
        if (assetThreatCtx.chart) {
            assetThreatCtx.chart.destroy();
        }
        
        assetThreatCtx.chart = new Chart(assetThreatCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: ['A1', 'C3', 'B2'],
                datasets: [{
                    label: '이상 징후 수',
                    data: [3, 2, 1],
                    backgroundColor: 'rgba(56, 178, 172, 0.7)',
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // Anomaly Trend Chart (for reports section)
    const anomalyTrendCtx = document.getElementById('anomalyTrendChart');
    if (anomalyTrendCtx && anomalyTrendCtx.getContext) {
        // Destroy existing chart instance if it exists
        if (anomalyTrendCtx.chart) {
            anomalyTrendCtx.chart.destroy();
        }
        
        anomalyTrendCtx.chart = new Chart(anomalyTrendCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: ['1월', '2월', '3월', '4월', '5월', '6월', '7월', '8월', '9월', '10월'],
                datasets: [{
                    label: '이상 징후 수',
                    data: [12, 19, 3, 5, 2, 8, 11, 14, 9, 7],
                    borderColor: 'rgb(72, 187, 120)',
                    backgroundColor: 'rgba(72, 187, 120, 0.1)',
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // Asset Status Chart (for reports section)
    const assetStatusReportCtx = document.getElementById('assetStatusChart');
    if (assetStatusReportCtx && assetStatusReportCtx.getContext && !assetStatusReportCtx.classList.contains('doughnut-chart')) {
        // Destroy existing chart instance if it exists
        if (assetStatusReportCtx.chart) {
            assetStatusReportCtx.chart.destroy();
        }
        
        assetStatusReportCtx.chart = new Chart(assetStatusReportCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                datasets: [{
                    data: [80, 15, 5],
                    backgroundColor: [
                        'rgba(72, 187, 120, 0.7)',  // normal
                        'rgba(237, 137, 54, 0.7)',   // warning
                        'rgba(229, 62, 62, 0.7)'     // danger
                    ],
                    borderWidth: 0
                }],
                labels: ['정상', '경고', '이상']
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                }
            }
        });
    }
}

// Handle responsive layout changes
window.addEventListener('resize', function() {
    const sidebar = document.getElementById('sidebarNav');
    if (!sidebar) return;
    
    if (window.innerWidth >= 992) {
        // On desktop, ensure sidebar is always visible
        sidebar.classList.remove('show');
        sidebar.classList.add('collapse', 'show');
    } else {
        // On mobile, remove 'show' class to properly hide sidebar
        sidebar.classList.remove('show');
        sidebar.classList.remove('show');
    }
});