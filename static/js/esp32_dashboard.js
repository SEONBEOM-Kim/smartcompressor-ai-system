// ESP32 대시보드 메인 로직

// 전역 변수
let autoRefreshInterval = null;
let currentData = [];
let currentDeviceId = '';

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    console.log('[Dashboard] 페이지 로드 완료');
    initializeDashboard();
});

// 대시보드 초기화
async function initializeDashboard() {
    try {
        console.log('[Dashboard] 대시보드 초기화 시작');
        
        // 차트 초기화
        ESP32Charts.initializeAllCharts();
        
        // AI 분석 초기화
        if (window.ESP32AI) {
            await ESP32AI.loadAIAnalysis();
            ESP32AI.startAIAutoUpdate();
        }
        
        // 디바이스 목록 로드
        await loadDevices();
        
        // 초기 데이터 로드
        await loadData();
        
        // 자동 새로고침 시작
        startAutoRefresh();
        
        console.log('[Dashboard] 대시보드 초기화 완료');
        
    } catch (error) {
        console.error('[Dashboard] 초기화 실패:', error);
        showAlert('대시보드 초기화에 실패했습니다: ' + error.message, 'danger');
    }
}

// 디바이스 목록 로드
async function loadDevices() {
    try {
        const devices = await ESP32API.fetchDevices();
        const select = document.getElementById('sensorSelect');
        
        if (!select) return;
        
        // 기존 옵션 제거 (전체 센서 제외)
        while (select.children.length > 1) {
            select.removeChild(select.lastChild);
        }
        
        // 디바이스 옵션 추가
        devices.forEach(device => {
            const option = document.createElement('option');
            option.value = device.device_id;
            option.textContent = device.device_id;
            select.appendChild(option);
        });
        
        console.log(`[Dashboard] ${devices.length}개 디바이스 로드됨`);
        
    } catch (error) {
        console.error('[Dashboard] 디바이스 로드 실패:', error);
    }
}

// 데이터 로드
async function loadData() {
    try {
        console.log('[Dashboard] 데이터 로드 시작');
        
        // 로딩 상태 표시
        updateConnectionStatus('warning', '연결 중...');
        showLoading('recentData', '데이터 로딩 중...');
        
        // 설정값 가져오기
        const limit = document.getElementById('dataLimit')?.value || 100;
        const hours = document.getElementById('timeRange')?.value || 24;
        const deviceId = document.getElementById('sensorSelect')?.value || '';
        
        // API 호출
        const data = await ESP32API.fetchRecentDataCached(parseInt(limit), parseInt(hours), deviceId);
        
        if (!Array.isArray(data)) {
            throw new Error('잘못된 데이터 형식입니다.');
        }
        
        currentData = data;
        currentDeviceId = deviceId;
        
        // 대시보드 업데이트
        updateDashboard(data);
        
        // 연결 상태 업데이트
        updateConnectionStatus('online', '연결됨');
        
        console.log(`[Dashboard] ${data.length}개 데이터 로드 완료`);
        
    } catch (error) {
        console.error('[Dashboard] 데이터 로드 실패:', error);
        updateConnectionStatus('offline', '연결 실패');
        showError('recentData', '데이터 로드 실패: ' + error.message);
        ESP32API.handleApiError(error, '데이터 로드');
    }
}

// 대시보드 업데이트
function updateDashboard(data) {
    if (!Array.isArray(data) || data.length === 0) {
        showAlert('데이터가 없습니다.', 'warning');
        return;
    }
    
    try {
        console.log(`[Dashboard] 대시보드 업데이트 시작 (${data.length}개 데이터)`);
        
        // 최신 데이터로 실시간 메트릭 업데이트
        const latest = data[0];
        updateRealtimeMetrics(latest);
        
        // 상태 바 업데이트
        const deviceIds = extractDeviceIds(data);
        updateDeviceStatus(deviceIds.length, new Date().toLocaleTimeString(), data.length);
        
        // 압축기 상태 분석
        const compressorStats = calculateCompressorStats(data);
        updateCompressorStatusUI(compressorStats);
        
        // 차트 업데이트
        ESP32Charts.updateAllCharts(data);
        
        // 최근 데이터 테이블 업데이트
        updateRecentDataTable(data);
        
        // 업데이트 시간 표시
        const updateTimeEl = document.getElementById('updateTime');
        if (updateTimeEl) {
            updateTimeEl.textContent = new Date().toLocaleTimeString();
        }
        
        console.log('[Dashboard] 대시보드 업데이트 완료');
        
    } catch (error) {
        console.error('[Dashboard] 대시보드 업데이트 실패:', error);
        showAlert('대시보드 업데이트에 실패했습니다: ' + error.message, 'danger');
    }
}

// 최근 데이터 테이블 업데이트
function updateRecentDataTable(data) {
    const container = document.getElementById('recentData');
    if (!container) return;
    
    try {
        // 최근 10개 데이터만 표시
        const recentData = data.slice(0, 10);
        
        if (recentData.length === 0) {
            container.innerHTML = '<div class="alert alert-warning">데이터가 없습니다.</div>';
            return;
        }
        
        // 테이블 생성
        let tableHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>시간</th>
                        <th>디바이스</th>
                        <th>RMS</th>
                        <th>데시벨</th>
                        <th>압축기</th>
                        <th>이상점수</th>
                        <th>효율성</th>
                        <th>소리유형</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        recentData.forEach(item => {
            const decibelLevel = rmsToDecibel(item.rms_energy);
            const compressorState = isCompressorOn(decibelLevel) ? 'ON' : 'OFF';
            const soundTypeName = getSoundTypeName(item.sound_type);
            const timestamp = formatTime(item.timestamp || item.server_timestamp);
            
            tableHTML += `
                <tr>
                    <td>${timestamp}</td>
                    <td>${item.device_id || '-'}</td>
                    <td>${formatNumber(item.rms_energy, 2)}</td>
                    <td>${formatNumber(decibelLevel, 1)} dB</td>
                    <td style="color: ${compressorState === 'ON' ? '#e74c3c' : '#27ae60'}">${compressorState}</td>
                    <td>${formatNumber(item.anomaly_score, 3)}</td>
                    <td>${formatNumber(item.efficiency_score, 3)}</td>
                    <td style="color: ${getSoundTypeColor(item.sound_type)}">${soundTypeName}</td>
                </tr>
            `;
        });
        
        tableHTML += '</tbody></table>';
        container.innerHTML = tableHTML;
        
    } catch (error) {
        console.error('[Dashboard] 데이터 테이블 업데이트 실패:', error);
        container.innerHTML = '<div class="alert alert-danger">테이블 생성에 실패했습니다.</div>';
    }
}

// 센서 변경
function changeSensor() {
    const select = document.getElementById('sensorSelect');
    if (select) {
        currentDeviceId = select.value;
        loadData();
    }
}

// 데이터 새로고침
async function refreshData() {
    console.log('[Dashboard] 수동 새로고침 시작');
    await loadData();
}

// 자동 새로고침 시작
function startAutoRefresh() {
    if (autoRefreshInterval) {
        console.log('[Dashboard] 자동 새로고침이 이미 실행 중입니다.');
        return;
    }
    
    console.log('[Dashboard] 자동 새로고침 시작 (30초 간격)');
    autoRefreshInterval = setInterval(async () => {
        try {
            await loadData();
        } catch (error) {
            console.error('[Dashboard] 자동 새로고침 실패:', error);
        }
    }, 30000); // 30초 간격
}

// 자동 새로고침 중지
function stopAutoRefresh() {
    if (autoRefreshInterval) {
        console.log('[Dashboard] 자동 새로고침 중지');
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// 페이지 언로드 시 정리
window.addEventListener('beforeunload', function() {
    stopAutoRefresh();
    ESP32Charts.destroyCharts();
    if (window.ESP32AI) {
        ESP32AI.stopAIAutoUpdate();
        ESP32AI.destroyAICharts();
    }
});

// 윈도우 리사이즈 시 차트 리사이즈
window.addEventListener('resize', function() {
    ESP32Charts.resizeCharts();
    if (window.ESP32AI) {
        ESP32AI.resizeAICharts();
    }
});

// 전역 함수로 노출 (HTML에서 호출용)
window.changeSensor = changeSensor;
window.loadData = loadData;
window.refreshData = refreshData;
window.startAutoRefresh = startAutoRefresh;
window.stopAutoRefresh = stopAutoRefresh;
