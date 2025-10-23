// ESP32 AI 분석 결과 시각화 모듈

// AI 분석 관련 전역 변수
let aiAnalysisData = [];
let aiCharts = {};
let aiUpdateInterval = null;

// AI 분석 결과 로드
async function loadAIAnalysis() {
    try {
        console.log('[AI] AI 분석 결과 로드 시작');
        
        const response = await fetch('/api/esp32/analysis/recent?limit=100&hours=24');
        const data = await response.json();
        
        if (data.success) {
            aiAnalysisData = data.data;
            updateAIAnalysisDisplay();
            console.log(`[AI] ${aiAnalysisData.length}개 AI 분석 결과 로드 완료`);
        } else {
            console.error('[AI] AI 분석 결과 로드 실패:', data.error);
        }
        
    } catch (error) {
        console.error('[AI] AI 분석 결과 로드 오류:', error);
    }
}

// AI 분석 결과 표시 업데이트
function updateAIAnalysisDisplay() {
    if (aiAnalysisData.length === 0) {
        showAIMessage('AI 분석 데이터가 없습니다.', 'warning');
        return;
    }
    
    // 최신 분석 결과
    const latestAnalysis = aiAnalysisData[0];
    updateLatestAIAnalysis(latestAnalysis);
    
    // AI 분석 차트 업데이트
    updateAIAnalysisCharts();
    
    // 이상 감지 알림
    checkAnomalyAlerts();
}

// 최신 AI 분석 결과 표시
function updateLatestAIAnalysis(analysis) {
    const {
        is_anomaly,
        anomaly_score,
        confidence,
        severity,
        recommendation,
        analyzed_at
    } = analysis;
    
    // AI 상태 표시
    const aiStatusEl = document.getElementById('aiStatus');
    if (aiStatusEl) {
        aiStatusEl.textContent = is_anomaly ? '⚠️ 이상 감지' : '✅ 정상';
        aiStatusEl.className = `ai-status ${is_anomaly ? 'anomaly' : 'normal'}`;
    }
    
    // 이상 점수 표시
    const anomalyScoreEl = document.getElementById('aiAnomalyScore');
    if (anomalyScoreEl) {
        anomalyScoreEl.textContent = (anomaly_score * 100).toFixed(1) + '%';
        anomalyScoreEl.className = `anomaly-score ${getAnomalyScoreClass(anomaly_score)}`;
    }
    
    // 신뢰도 표시
    const confidenceEl = document.getElementById('aiConfidence');
    if (confidenceEl) {
        confidenceEl.textContent = (confidence * 100).toFixed(1) + '%';
    }
    
    // 심각도 표시
    const severityEl = document.getElementById('aiSeverity');
    if (severityEl) {
        severityEl.textContent = getSeverityText(severity);
        severityEl.className = `severity ${severity || 'normal'}`;
    }
    
    // 권장사항 표시
    const recommendationEl = document.getElementById('aiRecommendation');
    if (recommendationEl) {
        recommendationEl.textContent = recommendation || '정상 운영 중';
    }
    
    // 분석 시간 표시
    const analysisTimeEl = document.getElementById('aiAnalysisTime');
    if (analysisTimeEl) {
        const analysisTime = new Date(analyzed_at);
        analysisTimeEl.textContent = analysisTime.toLocaleString('ko-KR');
    }
}

// AI 분석 차트 업데이트
function updateAIAnalysisCharts() {
    if (aiAnalysisData.length === 0) return;
    
    // 이상 점수 차트
    updateAnomalyScoreChart();
    
    // 이상 감지 빈도 차트
    updateAnomalyFrequencyChart();
    
    // 신뢰도 분포 차트
    updateConfidenceDistributionChart();
}

// 이상 점수 차트 업데이트
function updateAnomalyScoreChart() {
    const ctx = document.getElementById('aiAnomalyChart');
    if (!ctx) return;
    
    // 최근 50개 데이터
    const recentData = aiAnalysisData.slice(0, 50).reverse();
    const labels = recentData.map((_, i) => i + 1);
    const anomalyScores = recentData.map(d => d.anomaly_score * 100);
    const isAnomalies = recentData.map(d => d.is_anomaly);
    
    // 차트 데이터 설정
    const chartData = {
        labels: labels,
        datasets: [{
            label: '이상 점수 (%)',
            data: anomalyScores,
            borderColor: '#e74c3c',
            backgroundColor: 'rgba(231, 76, 60, 0.1)',
            tension: 0.1,
            fill: true
        }, {
            label: '이상 감지',
            data: isAnomalies.map(a => a ? 100 : 0),
            borderColor: '#f39c12',
            backgroundColor: 'rgba(243, 156, 18, 0.1)',
            tension: 0.1,
            fill: false,
            yAxisID: 'y1'
        }]
    };
    
    // 차트 업데이트 또는 생성
    if (aiCharts.anomaly) {
        aiCharts.anomaly.data = chartData;
        aiCharts.anomaly.update('none');
    } else {
        aiCharts.anomaly = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: '이상 점수 (%)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        min: 0,
                        max: 100,
                        grid: {
                            drawOnChartArea: false,
                        },
                        title: {
                            display: true,
                            text: '이상 감지'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }
}

// 이상 감지 빈도 차트 업데이트
function updateAnomalyFrequencyChart() {
    const ctx = document.getElementById('aiFrequencyChart');
    if (!ctx) return;
    
    // 시간대별 이상 감지 빈도 계산
    const hourlyAnomalies = {};
    const hourlyTotal = {};
    
    aiAnalysisData.forEach(analysis => {
        const hour = new Date(analysis.analyzed_at).getHours();
        hourlyTotal[hour] = (hourlyTotal[hour] || 0) + 1;
        if (analysis.is_anomaly) {
            hourlyAnomalies[hour] = (hourlyAnomalies[hour] || 0) + 1;
        }
    });
    
    const hours = Array.from({length: 24}, (_, i) => i);
    const anomalyCounts = hours.map(h => hourlyAnomalies[h] || 0);
    const totalCounts = hours.map(h => hourlyTotal[h] || 0);
    const anomalyRates = hours.map(h => 
        totalCounts[h] > 0 ? (anomalyCounts[h] / totalCounts[h] * 100) : 0
    );
    
    const chartData = {
        labels: hours.map(h => h + '시'),
        datasets: [{
            label: '이상 감지 빈도 (%)',
            data: anomalyRates,
            backgroundColor: 'rgba(231, 76, 60, 0.6)',
            borderColor: '#e74c3c',
            borderWidth: 1
        }]
    };
    
    if (aiCharts.frequency) {
        aiCharts.frequency.data = chartData;
        aiCharts.frequency.update('none');
    } else {
        aiCharts.frequency = new Chart(ctx, {
            type: 'bar',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: '이상 감지 비율 (%)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }
}

// 신뢰도 분포 차트 업데이트
function updateConfidenceDistributionChart() {
    const ctx = document.getElementById('aiConfidenceChart');
    if (!ctx) return;
    
    const confidences = aiAnalysisData.map(d => d.confidence * 100);
    
    // 히스토그램 데이터 생성
    const bins = 10;
    const binSize = 100 / bins;
    const histogram = Array(bins).fill(0);
    
    confidences.forEach(conf => {
        const binIndex = Math.min(Math.floor(conf / binSize), bins - 1);
        histogram[binIndex]++;
    });
    
    const labels = Array.from({length: bins}, (_, i) => 
        `${(i * binSize).toFixed(0)}-${((i + 1) * binSize).toFixed(0)}%`
    );
    
    const chartData = {
        labels: labels,
        datasets: [{
            label: '신뢰도 분포',
            data: histogram,
            backgroundColor: 'rgba(52, 152, 219, 0.6)',
            borderColor: '#3498db',
            borderWidth: 1
        }]
    };
    
    if (aiCharts.confidence) {
        aiCharts.confidence.data = chartData;
        aiCharts.confidence.update('none');
    } else {
        aiCharts.confidence = new Chart(ctx, {
            type: 'bar',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: '빈도'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }
}

// 이상 감지 알림 확인
function checkAnomalyAlerts() {
    const recentAnomalies = aiAnalysisData.filter(d => d.is_anomaly).slice(0, 5);
    
    recentAnomalies.forEach(anomaly => {
        if (anomaly.anomaly_score > 0.7) {
            showAIAlert(anomaly);
        }
    });
}

// AI 알림 표시
function showAIAlert(anomaly) {
    const alertId = `ai-alert-${anomaly.analyzed_at}`;
    
    // 중복 알림 방지
    if (document.getElementById(alertId)) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.id = alertId;
    alertDiv.className = 'ai-alert alert-danger';
    alertDiv.innerHTML = `
        <div class="alert-header">
            <strong>🚨 AI 이상 감지</strong>
            <button type="button" class="close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
        <div class="alert-body">
            <p><strong>이상 점수:</strong> ${(anomaly.anomaly_score * 100).toFixed(1)}%</p>
            <p><strong>심각도:</strong> ${getSeverityText(anomaly.severity)}</p>
            <p><strong>권장사항:</strong> ${anomaly.recommendation || '상세 점검 필요'}</p>
            <p><strong>시간:</strong> ${new Date(anomaly.analyzed_at).toLocaleString('ko-KR')}</p>
        </div>
    `;
    
    const alertsContainer = document.getElementById('alerts');
    if (alertsContainer) {
        alertsContainer.appendChild(alertDiv);
        
        // 10초 후 자동 제거
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.parentNode.removeChild(alertDiv);
            }
        }, 10000);
    }
}

// AI 메시지 표시
function showAIMessage(message, type = 'info') {
    const alertsContainer = document.getElementById('alerts');
    if (!alertsContainer) return;
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} ai-message`;
    alertDiv.textContent = message;
    
    alertsContainer.appendChild(alertDiv);
    
    // 5초 후 자동 제거
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// 유틸리티 함수들
function getAnomalyScoreClass(score) {
    if (score >= 0.8) return 'critical';
    if (score >= 0.6) return 'high';
    if (score >= 0.4) return 'medium';
    return 'low';
}

function getSeverityText(severity) {
    const severityMap = {
        'critical': '심각',
        'high': '높음',
        'medium': '보통',
        'low': '낮음',
        'normal': '정상'
    };
    return severityMap[severity] || '알 수 없음';
}

// AI 분석 자동 업데이트 시작
function startAIAutoUpdate() {
    if (aiUpdateInterval) return;
    
    console.log('[AI] AI 분석 자동 업데이트 시작');
    aiUpdateInterval = setInterval(async () => {
        try {
            await loadAIAnalysis();
        } catch (error) {
            console.error('[AI] 자동 업데이트 오류:', error);
        }
    }, 30000); // 30초 간격
}

// AI 분석 자동 업데이트 중지
function stopAIAutoUpdate() {
    if (aiUpdateInterval) {
        console.log('[AI] AI 분석 자동 업데이트 중지');
        clearInterval(aiUpdateInterval);
        aiUpdateInterval = null;
    }
}

// AI 차트 리사이즈
function resizeAICharts() {
    Object.values(aiCharts).forEach(chart => {
        if (chart && typeof chart.resize === 'function') {
            chart.resize();
        }
    });
}

// AI 차트 파괴
function destroyAICharts() {
    Object.values(aiCharts).forEach(chart => {
        if (chart && typeof chart.destroy === 'function') {
            chart.destroy();
        }
    });
    Object.keys(aiCharts).forEach(key => delete aiCharts[key]);
}

// AI 모듈 내보내기
window.ESP32AI = {
    loadAIAnalysis,
    updateAIAnalysisDisplay,
    startAIAutoUpdate,
    stopAIAutoUpdate,
    resizeAICharts,
    destroyAICharts,
    showAIAlert,
    showAIMessage
};
