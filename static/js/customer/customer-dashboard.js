// 고객 대시보드 모듈 JavaScript
class CustomerDashboard {
    constructor() {
        this.lastCheckTime = new Date();
        this.continuousDays = 15;
        this.anomalyCount = 0;
        this.diagnosisData = this.generateDiagnosisData();
        this.init();
    }
    
    init() {
        this.updateLastCheckTime();
        this.startRealTimeUpdates();
        this.initDiagnosisChart();
        this.updateContinuousDays();
    }
    
    updateLastCheckTime() {
        const now = new Date();
        const diff = Math.floor((now - this.lastCheckTime) / 1000);
        
        let timeText;
        if (diff < 60) {
            timeText = '방금 전';
        } else if (diff < 3600) {
            timeText = `${Math.floor(diff / 60)}분 전`;
        } else {
            timeText = `${Math.floor(diff / 3600)}시간 전`;
        }
        
        const lastCheckElement = document.getElementById('lastCheck');
        if (lastCheckElement) {
            lastCheckElement.textContent = timeText;
        }
    }
    
    startRealTimeUpdates() {
        // 30초마다 업데이트
        setInterval(() => {
            this.updateLastCheckTime();
            this.simulateRealTimeCheck();
        }, 30000);
    }
    
    simulateRealTimeCheck() {
        // 실제로는 서버에서 데이터를 가져옴
        this.lastCheckTime = new Date();
        this.updateLastCheckTime();
        
        // 상태 업데이트 애니메이션
        this.animateStatusUpdate();
    }
    
    animateStatusUpdate() {
        const statusIndicators = document.querySelectorAll('.status-indicator i');
        statusIndicators.forEach(indicator => {
            indicator.style.transform = 'scale(1.1)';
            indicator.style.transition = 'transform 0.3s ease';
            
            setTimeout(() => {
                indicator.style.transform = 'scale(1)';
            }, 300);
        });
    }
    
    updateContinuousDays() {
        // 실제로는 서버에서 데이터를 가져옴
        const daysElement = document.querySelector('.card-title.text-warning');
        if (daysElement) {
            daysElement.textContent = `연속 정상 운영 ${this.continuousDays}일`;
        }
    }
    
    generateDiagnosisData() {
        // 최근 7일 진단 데이터 생성
        const data = [];
        const today = new Date();
        
        for (let i = 6; i >= 0; i--) {
            const date = new Date(today);
            date.setDate(date.getDate() - i);
            
            data.push({
                date: date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' }),
                normal: Math.floor(Math.random() * 20) + 15,
                anomaly: Math.floor(Math.random() * 3)
            });
        }
        
        return data;
    }
    
    initDiagnosisChart() {
        const ctx = document.getElementById('diagnosisChart');
        if (!ctx) return;
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.diagnosisData.map(d => d.date),
                datasets: [{
                    label: '정상 진단',
                    data: this.diagnosisData.map(d => d.normal),
                    borderColor: 'rgb(40, 167, 69)',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.1
                }, {
                    label: '이상 감지',
                    data: this.diagnosisData.map(d => d.anomaly),
                    borderColor: 'rgb(220, 53, 69)',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: '일별 진단 현황'
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
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    // 고객 대시보드 섹션이 있을 때만 초기화
    if (document.getElementById('customer-dashboard-section')) {
        new CustomerDashboard();
    }
});
