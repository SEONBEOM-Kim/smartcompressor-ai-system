// ESP32 API 통신 모듈

// API 기본 설정
const API_CONFIG = {
    baseUrl: '/api/esp32',
    timeout: 10000,
    retryAttempts: 3
};

// API 호출 함수
async function apiCall(endpoint, options = {}) {
    const url = `${API_CONFIG.baseUrl}${endpoint}`;
    const config = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        timeout: API_CONFIG.timeout,
        ...options
    };
    
    let lastError;
    
    for (let attempt = 1; attempt <= API_CONFIG.retryAttempts; attempt++) {
        try {
            console.log(`[API] 시도 ${attempt}/${API_CONFIG.retryAttempts}: ${url}`);
            
            const response = await fetch(url, config);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const text = await response.text();
                console.error('[API] JSON이 아닌 응답:', text.substring(0, 200));
                throw new Error('서버가 JSON이 아닌 응답을 반환했습니다.');
            }
            
            const data = await response.json();
            console.log(`[API] 성공: ${url}`, data);
            return data;
            
        } catch (error) {
            lastError = error;
            console.warn(`[API] 시도 ${attempt} 실패:`, error.message);
            
            if (attempt < API_CONFIG.retryAttempts) {
                const delay = Math.pow(2, attempt) * 1000; // 지수 백오프
                console.log(`[API] ${delay}ms 후 재시도...`);
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }
    
    throw lastError;
}

// 최근 센서 데이터 조회
async function fetchRecentData(limit = 100, hours = 24, deviceId = '') {
    try {
        let endpoint = `/features/recent?limit=${limit}&hours=${hours}`;
        if (deviceId) {
            endpoint += `&device_id=${encodeURIComponent(deviceId)}`;
        }
        
        const data = await apiCall(endpoint);
        
        if (!data.success) {
            throw new Error(data.message || '데이터 조회 실패');
        }
        
        return data.data || [];
        
    } catch (error) {
        console.error('[API] 최근 데이터 조회 실패:', error);
        throw error;
    }
}

// 디바이스 목록 조회
async function fetchDevices() {
    try {
        const data = await apiCall('/devices');
        
        if (!data.success) {
            throw new Error(data.message || '디바이스 목록 조회 실패');
        }
        
        return data.devices || [];
        
    } catch (error) {
        console.error('[API] 디바이스 목록 조회 실패:', error);
        throw error;
    }
}

// 통계 데이터 조회
async function fetchStats() {
    try {
        const data = await apiCall('/stats');
        
        if (!data.success) {
            throw new Error(data.message || '통계 조회 실패');
        }
        
        return data.stats || {};
        
    } catch (error) {
        console.error('[API] 통계 조회 실패:', error);
        throw error;
    }
}

// 센서 데이터 업로드 (테스트용)
async function uploadSensorData(sensorData) {
    try {
        const data = await apiCall('/features', {
            method: 'POST',
            body: JSON.stringify(sensorData)
        });
        
        return data;
        
    } catch (error) {
        console.error('[API] 센서 데이터 업로드 실패:', error);
        throw error;
    }
}

// API 상태 확인
async function checkApiHealth() {
    try {
        const data = await apiCall('/features/recent?limit=1');
        return data.success === true;
    } catch (error) {
        console.error('[API] 상태 확인 실패:', error);
        return false;
    }
}

// 에러 처리 함수
function handleApiError(error, context = '') {
    console.error(`[API] ${context} 오류:`, error);
    
    let message = '알 수 없는 오류가 발생했습니다.';
    
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
        message = '네트워크 연결을 확인해주세요.';
    } else if (error.message.includes('HTTP 404')) {
        message = '요청한 데이터를 찾을 수 없습니다.';
    } else if (error.message.includes('HTTP 500')) {
        message = '서버 내부 오류가 발생했습니다.';
    } else if (error.message.includes('timeout')) {
        message = '요청 시간이 초과되었습니다.';
    } else if (error.message) {
        message = error.message;
    }
    
    showAlert(message, 'danger');
    return message;
}

// 데이터 캐싱
const dataCache = {
    cache: new Map(),
    maxAge: 30000, // 30초
    
    set(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
    },
    
    get(key) {
        const item = this.cache.get(key);
        if (!item) return null;
        
        const age = Date.now() - item.timestamp;
        if (age > this.maxAge) {
            this.cache.delete(key);
            return null;
        }
        
        return item.data;
    },
    
    clear() {
        this.cache.clear();
    }
};

// 캐시된 데이터 조회
async function fetchRecentDataCached(limit = 100, hours = 24, deviceId = '') {
    const cacheKey = `recent_${limit}_${hours}_${deviceId}`;
    
    // 캐시에서 먼저 확인
    const cached = dataCache.get(cacheKey);
    if (cached) {
        console.log('[API] 캐시된 데이터 사용');
        return cached;
    }
    
    // API에서 데이터 조회
    const data = await fetchRecentData(limit, hours, deviceId);
    
    // 캐시에 저장
    dataCache.set(cacheKey, data);
    
    return data;
}

// API 모듈 내보내기
window.ESP32API = {
    fetchRecentData,
    fetchRecentDataCached,
    fetchDevices,
    fetchStats,
    uploadSensorData,
    checkApiHealth,
    handleApiError,
    dataCache
};
