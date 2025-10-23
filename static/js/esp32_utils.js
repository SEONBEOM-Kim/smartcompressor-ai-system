// ESP32 대시보드 유틸리티 함수들

// RMS를 데시벨로 변환하는 함수
function rmsToDecibel(rms) {
    if (rms <= 0) return 0;
    // 20 * log10(rms) 공식 사용
    return 20 * Math.log10(rms);
}

// 알림 표시 함수
function showAlert(message, type = 'info') {
    const alertsContainer = document.getElementById('alerts');
    if (!alertsContainer) return;

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    alertsContainer.appendChild(alertDiv);
    
    // 5초 후 자동 제거
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// 시간 포맷팅 함수
function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('ko-KR');
}

// 숫자 포맷팅 함수
function formatNumber(num, decimals = 2) {
    if (typeof num !== 'number' || isNaN(num)) return '-';
    return num.toFixed(decimals);
}

// 소리 유형 이름 변환
function getSoundTypeName(soundType) {
    const soundTypeNames = ['정적', '압축기', '팬', '이상음', '기타'];
    const index = Math.round(soundType) || 0;
    return soundTypeNames[index] || '알 수 없음';
}

// 소리 유형 색상 반환
function getSoundTypeColor(soundType) {
    const soundTypeColors = ['#95a5a6', '#e74c3c', '#3498db', '#f39c12', '#9b59b6'];
    const index = Math.round(soundType) || 0;
    return soundTypeColors[index] || '#95a5a6';
}

// 강도 레벨 색상 반환
function getIntensityColor(intensityLevel) {
    const intensity = intensityLevel * 100;
    if (intensity > 70) return '#e74c3c'; // 빨간색
    if (intensity > 40) return '#f39c12'; // 주황색
    return '#27ae60'; // 초록색
}

// 압축기 상태 판정 (45dB 기준)
function isCompressorOn(decibelLevel) {
    return decibelLevel >= 45;
}

// 데이터 유효성 검사
function isValidData(data) {
    return data && 
           typeof data === 'object' && 
           typeof data.rms_energy === 'number' && 
           !isNaN(data.rms_energy);
}

// 배열에서 최대값 찾기
function findMaxValue(array, key) {
    if (!Array.isArray(array) || array.length === 0) return 0;
    return Math.max(...array.map(item => item[key] || 0));
}

// 배열에서 최소값 찾기
function findMinValue(array, key) {
    if (!Array.isArray(array) || array.length === 0) return 0;
    return Math.min(...array.map(item => item[key] || 0));
}

// 배열에서 평균값 계산
function calculateAverage(array, key) {
    if (!Array.isArray(array) || array.length === 0) return 0;
    const sum = array.reduce((acc, item) => acc + (item[key] || 0), 0);
    return sum / array.length;
}

// 디바이스 ID 목록 추출
function extractDeviceIds(data) {
    if (!Array.isArray(data)) return [];
    const deviceIds = [...new Set(data.map(item => item.device_id).filter(id => id))];
    return deviceIds;
}

// 데이터 필터링
function filterDataByDevice(data, deviceId) {
    if (!deviceId || deviceId === '') return data;
    return data.filter(item => item.device_id === deviceId);
}

// 시간 범위 필터링
function filterDataByTimeRange(data, hours) {
    if (!hours || hours <= 0) return data;
    const cutoffTime = Date.now() - (hours * 60 * 60 * 1000);
    return data.filter(item => {
        const timestamp = item.timestamp || item.server_timestamp;
        return timestamp >= cutoffTime;
    });
}

// 로딩 상태 표시
function showLoading(elementId, message = '로딩 중...') {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    element.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            ${message}
        </div>
    `;
}

// 로딩 상태 숨기기
function hideLoading(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const loading = element.querySelector('.loading');
    if (loading) {
        loading.remove();
    }
}

// 에러 메시지 표시
function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    element.innerHTML = `
        <div class="alert alert-danger">
            <strong>오류:</strong> ${message}
        </div>
    `;
}

// 성공 메시지 표시
function showSuccess(elementId, message) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    element.innerHTML = `
        <div class="alert alert-success">
            <strong>성공:</strong> ${message}
        </div>
    `;
}

// 디바이스 상태 업데이트
function updateDeviceStatus(deviceCount, lastUpdate, dataCount) {
    const deviceCountEl = document.getElementById('deviceCount');
    const lastUpdateEl = document.getElementById('lastUpdate');
    const dataCountEl = document.getElementById('dataCount');
    
    if (deviceCountEl) deviceCountEl.textContent = deviceCount || 0;
    if (lastUpdateEl) lastUpdateEl.textContent = lastUpdate || '--:--';
    if (dataCountEl) dataCountEl.textContent = dataCount || 0;
}

// 연결 상태 업데이트
function updateConnectionStatus(status, message) {
    const statusEl = document.getElementById('connectionStatus');
    if (!statusEl) return;
    
    statusEl.textContent = message || status;
    statusEl.className = `status-value status-${status}`;
}

// 실시간 메트릭 업데이트
function updateRealtimeMetrics(data) {
    if (!data || !isValidData(data)) return;
    
    const decibelLevel = rmsToDecibel(data.rms_energy);
    const compressorState = isCompressorOn(decibelLevel) ? 'ON' : 'OFF';
    
    // 메트릭 업데이트
    const metrics = {
        'currentRMS': formatNumber(data.rms_energy, 2),
        'currentDecibel': formatNumber(decibelLevel, 1) + ' dB',
        'currentCompressor': compressorState,
        'currentAnomaly': formatNumber(data.anomaly_score, 3),
        'currentEfficiency': formatNumber(data.efficiency_score, 3),
        'currentSoundType': getSoundTypeName(data.sound_type),
        'soundType': getSoundTypeName(data.sound_type),
        'intensityLevel': formatNumber((data.intensity_level || 0) * 100, 1) + '%'
    };
    
    // DOM 업데이트
    Object.entries(metrics).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
            
            // 특별한 스타일링
            if (id === 'soundType' || id === 'currentSoundType') {
                element.style.color = getSoundTypeColor(data.sound_type);
            } else if (id === 'intensityLevel') {
                element.style.color = getIntensityColor(data.intensity_level || 0);
            }
        }
    });
}

// 압축기 분석 통계 계산
function calculateCompressorStats(data) {
    if (!Array.isArray(data) || data.length === 0) {
        return {
            onCount: 0,
            offCount: 0,
            totalCount: 0,
            onPercentage: 0,
            offPercentage: 0
        };
    }
    
    let onCount = 0;
    let offCount = 0;
    
    data.forEach(item => {
        const decibelLevel = rmsToDecibel(item.rms_energy);
        if (isCompressorOn(decibelLevel)) {
            onCount++;
        } else {
            offCount++;
        }
    });
    
    const totalCount = data.length;
    const onPercentage = totalCount > 0 ? Math.round((onCount / totalCount) * 100) : 0;
    const offPercentage = totalCount > 0 ? Math.round((offCount / totalCount) * 100) : 0;
    
    return {
        onCount,
        offCount,
        totalCount,
        onPercentage,
        offPercentage
    };
}

// 압축기 상태 UI 업데이트
function updateCompressorStatusUI(stats) {
    const elements = {
        'onPercentage': stats.onPercentage + '%',
        'offPercentage': stats.offPercentage + '%',
        'totalMeasurements': stats.totalCount,
        'onCount': stats.onCount,
        'offCount': stats.offCount
    };
    
    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });
}
