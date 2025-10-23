// ESP32 차트 관리 모듈

// 차트 인스턴스 저장소
const charts = {};

// 차트 기본 옵션
const CHART_OPTIONS = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
        x: {
            type: 'linear',
            title: {
                display: true,
                text: '데이터 포인트'
            }
        },
        y: {
            beginAtZero: true
        }
    },
    plugins: {
        legend: {
            display: true,
            position: 'top'
        },
        tooltip: {
            mode: 'index',
            intersect: false
        }
    },
    interaction: {
        mode: 'nearest',
        axis: 'x',
        intersect: false
    }
};

// 압축기 상태 차트 초기화
function initializeCompressorChart() {
    const ctx = document.getElementById('compressorChart');
    if (!ctx) return;
    
    charts.compressor = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '압축기 상태',
                data: [],
                borderColor: '#e74c3c',
                backgroundColor: 'rgba(231, 76, 60, 0.1)',
                tension: 0.1,
                fill: true
            }]
        },
        options: {
            ...CHART_OPTIONS,
            scales: {
                ...CHART_OPTIONS.scales,
                y: {
                    ...CHART_OPTIONS.scales.y,
                    min: 0,
                    max: 1,
                    ticks: {
                        callback: function(value) {
                            return value === 1 ? 'ON' : 'OFF';
                        }
                    }
                }
            }
        }
    });
}

// RMS 차트 초기화
function initializeRmsChart() {
    const ctx = document.getElementById('rmsChart');
    if (!ctx) return;
    
    charts.rms = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'RMS 에너지',
                data: [],
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                tension: 0.1,
                fill: true
            }]
        },
        options: CHART_OPTIONS
    });
}

// 이상 점수 차트 초기화
function initializeAnomalyChart() {
    const ctx = document.getElementById('anomalyChart');
    if (!ctx) return;
    
    charts.anomaly = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '이상 점수',
                data: [],
                borderColor: '#f39c12',
                backgroundColor: 'rgba(243, 156, 18, 0.1)',
                tension: 0.1,
                fill: true
            }]
        },
        options: CHART_OPTIONS
    });
}

// 데시벨 차트 초기화
function initializeDecibelChart() {
    const ctx = document.getElementById('decibelChart');
    if (!ctx) return;
    
    charts.decibel = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '데시벨 (dB)',
                data: [],
                borderColor: '#e74c3c',
                backgroundColor: 'rgba(231, 76, 60, 0.1)',
                tension: 0.1,
                fill: true
            }]
        },
        options: CHART_OPTIONS
    });
}

// 압축기 상태 분석 차트 초기화
function initializeCompressorStateChart() {
    const ctx = document.getElementById('compressorStateChart');
    if (!ctx) return;
    
    charts.compressorState = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '압축기 상태',
                data: [],
                borderColor: '#e74c3c',
                backgroundColor: 'rgba(231, 76, 60, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.1
            }, {
                label: '데시벨 레벨',
                data: [],
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                borderWidth: 2,
                fill: false,
                tension: 0.1,
                yAxisID: 'y1'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    min: 0,
                    max: 1,
                    ticks: {
                        callback: function(value) {
                            if (value === 1) return 'ON';
                            if (value === 0) return 'OFF';
                            return '중간';
                        }
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    min: 0,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + ' dB';
                        }
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            if (context.datasetIndex === 0) {
                                const dataIndex = context.dataIndex;
                                const data = context.chart.data.datasets[1].data[dataIndex];
                                return `데시벨: ${data.toFixed(1)} dB`;
                            }
                            return '';
                        }
                    }
                }
            }
        }
    });
}

// 모든 차트 초기화
function initializeAllCharts() {
    console.log('[Charts] 차트 초기화 시작');
    
    try {
        initializeCompressorChart();
        initializeRmsChart();
        initializeAnomalyChart();
        initializeDecibelChart();
        initializeCompressorStateChart();
        
        console.log('[Charts] 모든 차트 초기화 완료');
    } catch (error) {
        console.error('[Charts] 차트 초기화 실패:', error);
    }
}

// 차트 데이터 업데이트
function updateChartData(chartName, labels, data) {
    if (!charts[chartName]) {
        console.warn(`[Charts] 차트 '${chartName}'가 존재하지 않습니다.`);
        return;
    }
    
    try {
        charts[chartName].data.labels = labels;
        charts[chartName].data.datasets[0].data = data;
        charts[chartName].update('none'); // 애니메이션 없이 업데이트
    } catch (error) {
        console.error(`[Charts] 차트 '${chartName}' 업데이트 실패:`, error);
    }
}

// 압축기 상태 차트 업데이트
function updateCompressorStateChart(data) {
    if (!charts.compressorState || !Array.isArray(data) || data.length === 0) return;
    
    try {
        // 최근 50개 데이터만 표시
        const limit = Math.min(50, data.length);
        const labels = Array.from({length: limit}, (_, i) => i + 1);
        
        // 압축기 상태 계산 (45dB 기준)
        const compressorStates = data.slice(0, limit).map(d => 
            rmsToDecibel(d.rms_energy) >= 45 ? 1 : 0
        );
        
        // 데시벨 값 계산
        const decibelValues = data.slice(0, limit).map(d => rmsToDecibel(d.rms_energy));
        
        // 차트 데이터 업데이트
        charts.compressorState.data.labels = labels;
        charts.compressorState.data.datasets[0].data = compressorStates;
        charts.compressorState.data.datasets[1].data = decibelValues;
        charts.compressorState.update('none');
        
    } catch (error) {
        console.error('[Charts] 압축기 상태 차트 업데이트 실패:', error);
    }
}

// 모든 차트 업데이트
function updateAllCharts(data) {
    if (!Array.isArray(data) || data.length === 0) return;
    
    try {
        // 최근 50개 데이터만 표시
        const limit = Math.min(50, data.length);
        const labels = Array.from({length: limit}, (_, i) => i + 1);
        
        // 데이터 추출
        const rmsData = data.slice(0, limit).map(d => d.rms_energy || 0);
        const anomalyData = data.slice(0, limit).map(d => d.anomaly_score || 0);
        const decibelData = data.slice(0, limit).map(d => rmsToDecibel(d.rms_energy));
        const compressorData = data.slice(0, limit).map(d => 
            rmsToDecibel(d.rms_energy) >= 45 ? 1 : 0
        );
        
        // 각 차트 업데이트
        updateChartData('rms', labels, rmsData);
        updateChartData('anomaly', labels, anomalyData);
        updateChartData('decibel', labels, decibelData);
        updateChartData('compressor', labels, compressorData);
        
        // 압축기 상태 차트는 별도 처리
        updateCompressorStateChart(data);
        
    } catch (error) {
        console.error('[Charts] 차트 업데이트 실패:', error);
    }
}

// 차트 리사이즈
function resizeCharts() {
    Object.values(charts).forEach(chart => {
        if (chart && typeof chart.resize === 'function') {
            chart.resize();
        }
    });
}

// 차트 파괴
function destroyCharts() {
    Object.values(charts).forEach(chart => {
        if (chart && typeof chart.destroy === 'function') {
            chart.destroy();
        }
    });
    Object.keys(charts).forEach(key => delete charts[key]);
}

// 차트 모듈 내보내기
window.ESP32Charts = {
    initializeAllCharts,
    updateAllCharts,
    updateCompressorStateChart,
    resizeCharts,
    destroyCharts,
    charts
};
