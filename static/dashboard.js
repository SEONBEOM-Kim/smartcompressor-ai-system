// 대시보드 JavaScript
class DashboardManager {
    constructor() {
        this.monitoringChart = null;
        this.refreshInterval = null;
        this.settings = {
            alertThreshold: 0.5,
            checkInterval: 60,
            emailAlerts: true,
            smsAlerts: false,
            kakaoAlerts: true
        };
        
        this.init();
    }

    init() {
        console.log('대시보드 초기화 시작');
        this.loadSettings();
        this.initChart();
        this.loadDashboardData();
        this.startAutoRefresh();
        this.setupEventListeners();
    }

    // 설정 로드
    loadSettings() {
        const savedSettings = localStorage.getItem('dashboardSettings');
        if (savedSettings) {
            this.settings = { ...this.settings, ...JSON.parse(savedSettings) };
        }
        this.applySettings();
    }

    // 설정 적용
    applySettings() {
        document.getElementById('alertThreshold').value = this.settings.alertThreshold;
        document.getElementById('checkInterval').value = this.settings.checkInterval;
        document.getElementById('emailAlerts').checked = this.settings.emailAlerts;
        document.getElementById('smsAlerts').checked = this.settings.smsAlerts;
        document.getElementById('kakaoAlerts').checked = this.settings.kakaoAlerts;
    }

    // 차트 초기화
    initChart() {
        const ctx = document.getElementById('monitoringChart').getContext('2d');
        this.monitoringChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '소음 레벨',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.1
                }, {
                    label: '이상 감지',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                    }
                }
            }
        });
    }

    // 대시보드 데이터 로드
    async loadDashboardData() {
        try {
            await Promise.all([
                this.loadCurrentStatus(),
                this.loadRecentDiagnosis(),
                this.loadAlerts(),
                this.loadStatistics(),
                this.loadMonitoringData()
            ]);
        } catch (error) {
            console.error('대시보드 데이터 로드 오류:', error);
        }
    }

    // 현재 상태 로드
    async loadCurrentStatus() {
        try {
            // 실제 API 호출 (현재는 시뮬레이션)
            const status = await this.simulateCurrentStatus();
            this.updateStatusDisplay(status);
        } catch (error) {
            console.error('상태 로드 오류:', error);
        }
    }

    // 상태 표시 업데이트
    updateStatusDisplay(status) {
        const statusIndicator = document.getElementById('statusIndicator');
        const statusText = document.getElementById('statusText');
        const lastCheck = document.getElementById('lastCheck');
        
        // 상태에 따른 색상 변경
        statusIndicator.className = `status-indicator status-${status.level}`;
        statusText.textContent = status.text;
        lastCheck.textContent = `마지막 확인: ${status.lastCheck}`;
        
        // 센서 데이터 업데이트
        document.getElementById('temperatureValue').textContent = status.temperature;
        document.getElementById('pressureValue').textContent = status.pressure;
        document.getElementById('vibrationValue').textContent = status.vibration;
    }

    // 최근 진단 결과 로드
    async loadRecentDiagnosis() {
        try {
            const diagnosis = await this.simulateRecentDiagnosis();
            this.updateRecentDiagnosis(diagnosis);
        } catch (error) {
            console.error('진단 결과 로드 오류:', error);
        }
    }

    // 진단 결과 표시 업데이트
    updateRecentDiagnosis(diagnosis) {
        const container = document.getElementById('recentDiagnosis');
        container.innerHTML = '';
        
        diagnosis.forEach(item => {
            const diagnosisItem = document.createElement('div');
            diagnosisItem.className = 'diagnosis-item';
            
            const statusClass = item.isAnomaly ? 'danger' : 'success';
            const statusText = item.isAnomaly ? '이상 감지' : '정상';
            
            diagnosisItem.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <div class="fw-bold">${item.timestamp}</div>
                        <div class="text-muted small">신뢰도: ${(item.confidence * 100).toFixed(1)}%</div>
                    </div>
                    <div>
                        <span class="badge bg-${statusClass} badge-status">${statusText}</span>
                    </div>
                </div>
            `;
            
            container.appendChild(diagnosisItem);
        });
    }

    // 알림 로드
    async loadAlerts() {
        try {
            const alerts = await this.simulateAlerts();
            this.updateAlerts(alerts);
        } catch (error) {
            console.error('알림 로드 오류:', error);
        }
    }

    // 알림 표시 업데이트
    updateAlerts(alerts) {
        const container = document.getElementById('alertCenter');
        container.innerHTML = '';
        
        if (alerts.length === 0) {
            container.innerHTML = '<div class="text-muted text-center">새로운 알림이 없습니다.</div>';
            return;
        }
        
        alerts.forEach(alert => {
            const alertItem = document.createElement('div');
            alertItem.className = `alert-item alert-${alert.type}`;
            
            alertItem.innerHTML = `
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <div class="fw-bold">${alert.title}</div>
                        <div class="small text-muted">${alert.message}</div>
                    </div>
                    <small class="text-muted">${alert.time}</small>
                </div>
            `;
            
            container.appendChild(alertItem);
        });
    }

    // 통계 로드
    async loadStatistics() {
        try {
            const stats = await this.simulateStatistics();
            this.updateStatistics(stats);
        } catch (error) {
            console.error('통계 로드 오류:', error);
        }
    }

    // 통계 표시 업데이트
    updateStatistics(stats) {
        document.getElementById('todayDiagnosis').textContent = stats.today;
        document.getElementById('weekDiagnosis').textContent = stats.week;
        document.getElementById('successRate').textContent = stats.successRate;
        document.getElementById('avgResponse').textContent = stats.avgResponse;
    }

    // 모니터링 데이터 로드
    async loadMonitoringData() {
        try {
            const data = await this.simulateMonitoringData();
            this.updateChart(data);
        } catch (error) {
            console.error('모니터링 데이터 로드 오류:', error);
        }
    }

    // 차트 업데이트
    updateChart(data) {
        if (!this.monitoringChart) return;
        
        this.monitoringChart.data.labels = data.labels;
        this.monitoringChart.data.datasets[0].data = data.noiseLevel;
        this.monitoringChart.data.datasets[1].data = data.anomalyDetection;
        this.monitoringChart.update();
    }

    // 자동 새로고침 시작
    startAutoRefresh() {
        const interval = this.settings.checkInterval * 1000;
        this.refreshInterval = setInterval(() => {
            this.loadDashboardData();
        }, interval);
    }

    // 이벤트 리스너 설정
    setupEventListeners() {
        // 설정 변경 감지
        document.getElementById('alertThreshold').addEventListener('change', (e) => {
            this.settings.alertThreshold = parseFloat(e.target.value);
            this.saveSettings();
        });
        
        document.getElementById('checkInterval').addEventListener('change', (e) => {
            this.settings.checkInterval = parseInt(e.target.value);
            this.saveSettings();
            this.restartAutoRefresh();
        });
    }

    // 설정 저장
    saveSettings() {
        localStorage.setItem('dashboardSettings', JSON.stringify(this.settings));
        console.log('설정 저장됨:', this.settings);
    }

    // 자동 새로고침 재시작
    restartAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
        }
        this.startAutoRefresh();
    }

    // 시뮬레이션 데이터 생성
    async simulateCurrentStatus() {
        return new Promise((resolve) => {
            setTimeout(() => {
                const levels = ['normal', 'warning', 'danger'];
                const level = levels[Math.floor(Math.random() * levels.length)];
                const statusTexts = {
                    normal: '정상 작동',
                    warning: '주의 필요',
                    danger: '위험 상태'
                };
                
                resolve({
                    level: level,
                    text: statusTexts[level],
                    lastCheck: '2분 전',
                    temperature: `${-18 + Math.random() * 2}°C`,
                    pressure: `${(2.5 + Math.random() * 0.5).toFixed(1)} bar`,
                    vibration: `${(0.3 + Math.random() * 0.2).toFixed(1)} mm/s`
                });
            }, 100);
        });
    }

    async simulateRecentDiagnosis() {
        return new Promise((resolve) => {
            setTimeout(() => {
                const diagnosis = [];
                for (let i = 0; i < 5; i++) {
                    const isAnomaly = Math.random() < 0.3;
                    diagnosis.push({
                        timestamp: new Date(Date.now() - i * 3600000).toLocaleString(),
                        isAnomaly: isAnomaly,
                        confidence: 0.7 + Math.random() * 0.3
                    });
                }
                resolve(diagnosis);
            }, 100);
        });
    }

    async simulateAlerts() {
        return new Promise((resolve) => {
            setTimeout(() => {
                const alerts = [];
                if (Math.random() < 0.5) {
                    alerts.push({
                        type: 'warning',
                        title: '압축기 진동 증가',
                        message: '평소보다 진동이 20% 증가했습니다.',
                        time: '5분 전'
                    });
                }
                if (Math.random() < 0.3) {
                    alerts.push({
                        type: 'info',
                        title: '정기 진단 완료',
                        message: '오늘의 정기 진단이 완료되었습니다.',
                        time: '1시간 전'
                    });
                }
                resolve(alerts);
            }, 100);
        });
    }

    async simulateStatistics() {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    today: Math.floor(Math.random() * 10) + 1,
                    week: Math.floor(Math.random() * 50) + 20,
                    successRate: (95 + Math.random() * 5).toFixed(1) + '%',
                    avgResponse: (1 + Math.random() * 2).toFixed(1) + 's'
                });
            }, 100);
        });
    }

    async simulateMonitoringData() {
        return new Promise((resolve) => {
            setTimeout(() => {
                const labels = [];
                const noiseLevel = [];
                const anomalyDetection = [];
                
                for (let i = 0; i < 20; i++) {
                    const time = new Date(Date.now() - (19 - i) * 300000);
                    labels.push(time.toLocaleTimeString());
                    noiseLevel.push(0.3 + Math.random() * 0.4);
                    anomalyDetection.push(Math.random() < 0.1 ? 0.8 : 0);
                }
                
                resolve({ labels, noiseLevel, anomalyDetection });
            }, 100);
        });
    }
}

// 전역 함수들
function refreshDashboard() {
    if (window.dashboardManager) {
        window.dashboardManager.loadDashboardData();
    }
}

function showSettings() {
    const modal = new bootstrap.Modal(document.getElementById('settingsModal'));
    modal.show();
}

function saveSettings() {
    if (window.dashboardManager) {
        window.dashboardManager.settings.emailAlerts = document.getElementById('emailAlerts').checked;
        window.dashboardManager.settings.smsAlerts = document.getElementById('smsAlerts').checked;
        window.dashboardManager.settings.kakaoAlerts = document.getElementById('kakaoAlerts').checked;
        window.dashboardManager.saveSettings();
        
        const modal = bootstrap.Modal.getInstance(document.getElementById('settingsModal'));
        modal.hide();
    }
}

// 페이지 로드 시 대시보드 초기화
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardManager = new DashboardManager();
});
