// Signalcraft 대시보드 JavaScript

// 전역 변수
let currentSection = 'overview';
let charts = {};
let refreshInterval;

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    loadDashboardData();
    setupEventListeners();
    startAutoRefresh();
});

// 대시보드 초기화
function initializeDashboard() {
    console.log('대시보드 초기화 중...');
    
    // 네비게이션 이벤트 리스너 설정
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const section = this.getAttribute('href').substring(1);
            showSection(section);
        });
    });
    
    // 차트 초기화
    initializeCharts();
    
    console.log('대시보드 초기화 완료');
}

// 섹션 표시
function showSection(sectionName) {
    // 모든 섹션 숨기기
    document.querySelectorAll('.dashboard-section').forEach(section => {
        section.style.display = 'none';
    });
    
    // 선택된 섹션 표시
    const targetSection = document.getElementById(sectionName);
    if (targetSection) {
        targetSection.style.display = 'block';
        currentSection = sectionName;
        
        // 섹션별 데이터 로드
        switch(sectionName) {
            case 'overview':
                loadOverviewData();
                break;
            case 'stores':
                loadStoresData();
                break;
            case 'devices':
                loadDevicesData();
                break;
            case 'analytics':
                loadAnalyticsData();
                break;
            case 'notifications':
                loadNotificationsData();
                break;
        }
    }
    
    // 네비게이션 활성화 상태 업데이트
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    const activeLink = document.querySelector(`[href="#${sectionName}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
}

// 차트 초기화
function initializeCharts() {
    // 에너지 소비량 차트
    const energyCtx = document.getElementById('energyChart');
    if (energyCtx) {
        charts.energy = new Chart(energyCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '에너지 소비량 (kW)',
                    data: [],
                    borderColor: '#4e73df',
                    backgroundColor: 'rgba(78, 115, 223, 0.1)',
                    tension: 0.4,
                    fill: true
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
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                }
            }
        });
    }
    
    // 디바이스 상태 차트
    const deviceStatusCtx = document.getElementById('deviceStatusChart');
    if (deviceStatusCtx) {
        charts.deviceStatus = new Chart(deviceStatusCtx, {
            type: 'doughnut',
            data: {
                labels: ['온라인', '오프라인', '점검중', '오류'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: ['#1cc88a', '#e74a3b', '#36b9cc', '#f6c23e'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    // 온도 트렌드 차트
    const temperatureCtx = document.getElementById('temperatureChart');
    if (temperatureCtx) {
        charts.temperature = new Chart(temperatureCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '온도 (°C)',
                    data: [],
                    borderColor: '#e74a3b',
                    backgroundColor: 'rgba(231, 74, 59, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false
                    }
                }
            }
        });
    }
    
    // 진동 분석 차트
    const vibrationCtx = document.getElementById('vibrationChart');
    if (vibrationCtx) {
        charts.vibration = new Chart(vibrationCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: '진동 레벨 (g)',
                    data: [],
                    backgroundColor: '#f6c23e',
                    borderColor: '#f6c23e',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // 전력 소비 패턴 차트
    const powerCtx = document.getElementById('powerChart');
    if (powerCtx) {
        charts.power = new Chart(powerCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: '전력 소비 (%)',
                    data: [],
                    backgroundColor: '#36b9cc',
                    borderColor: '#36b9cc',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
    
    // 이상 감지 패턴 차트
    const anomalyCtx = document.getElementById('anomalyChart');
    if (anomalyCtx) {
        charts.anomaly = new Chart(anomalyCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '이상 감지 수',
                    data: [],
                    borderColor: '#e74a3b',
                    backgroundColor: 'rgba(231, 74, 59, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// 대시보드 데이터 로드
async function loadDashboardData() {
    try {
        const response = await fetch('/api/dashboard/summary');
        const data = await response.json();
        
        if (data.success) {
            updateOverviewCards(data.summary);
            updateEnergyChart(data.energy_data);
            updateDeviceStatusChart(data.device_status);
        }
    } catch (error) {
        console.error('대시보드 데이터 로드 실패:', error);
        showAlert('데이터 로드에 실패했습니다.', 'danger');
    }
}

// 개요 데이터 로드
async function loadOverviewData() {
    try {
        const response = await fetch('/api/dashboard/summary');
        const data = await response.json();
        
        if (data.success) {
            updateOverviewCards(data.summary);
        }
    } catch (error) {
        console.error('개요 데이터 로드 실패:', error);
    }
}

// 매장 데이터 로드
async function loadStoresData() {
    try {
        const response = await fetch('/api/dashboard/stores');
        const data = await response.json();
        
        if (data.success) {
            updateStoresTable(data.stores);
        }
    } catch (error) {
        console.error('매장 데이터 로드 실패:', error);
    }
}

// 디바이스 데이터 로드
async function loadDevicesData() {
    try {
        const response = await fetch('/api/dashboard/devices');
        const data = await response.json();
        
        if (data.success) {
            updateDevicesTable(data.devices);
        }
    } catch (error) {
        console.error('디바이스 데이터 로드 실패:', error);
    }
}

// 분석 데이터 로드
async function loadAnalyticsData() {
    try {
        const response = await fetch('/api/dashboard/analytics');
        const data = await response.json();
        
        if (data.success) {
            updateAnalyticsCharts(data.analytics);
        }
    } catch (error) {
        console.error('분석 데이터 로드 실패:', error);
    }
}

// 알림 데이터 로드
async function loadNotificationsData() {
    try {
        const response = await fetch('/api/dashboard/notifications');
        const data = await response.json();
        
        if (data.success) {
            updateNotificationsTable(data.notifications);
        }
    } catch (error) {
        console.error('알림 데이터 로드 실패:', error);
    }
}

// 개요 카드 업데이트
function updateOverviewCards(summary) {
    if (summary.overview) {
        document.getElementById('totalStores').textContent = summary.overview.total_stores || 0;
        document.getElementById('onlineDevices').textContent = summary.overview.online_compressors || 0;
        document.getElementById('warningAlerts').textContent = summary.overview.warning_alerts || 0;
        document.getElementById('energyCost').textContent = `₩${(summary.overview.total_energy_cost || 0).toLocaleString()}`;
    }
}

// 에너지 차트 업데이트
function updateEnergyChart(energyData) {
    if (charts.energy && energyData) {
        charts.energy.data.labels = energyData.labels || [];
        charts.energy.data.datasets[0].data = energyData.values || [];
        charts.energy.update();
    }
}

// 디바이스 상태 차트 업데이트
function updateDeviceStatusChart(deviceStatus) {
    if (charts.deviceStatus && deviceStatus) {
        charts.deviceStatus.data.datasets[0].data = [
            deviceStatus.online || 0,
            deviceStatus.offline || 0,
            deviceStatus.maintenance || 0,
            deviceStatus.error || 0
        ];
        charts.deviceStatus.update();
    }
}

// 매장 테이블 업데이트
function updateStoresTable(stores) {
    const tbody = document.getElementById('storesTableBody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    stores.forEach(store => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${store.store_name}</td>
            <td>${store.address}</td>
            <td><span class="badge badge-${getStatusClass(store.status)}">${getStatusText(store.status)}</span></td>
            <td>${store.total_devices || 0}</td>
            <td>
                <div class="progress">
                    <div class="progress-bar" style="width: ${store.uptime_percentage || 0}%"></div>
                </div>
                <small>${(store.uptime_percentage || 0).toFixed(1)}%</small>
            </td>
            <td>${formatDate(store.last_activity)}</td>
            <td>
                <button class="btn btn-sm btn-primary me-1" onclick="editStore('${store.store_id}')">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteStore('${store.store_id}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// 디바이스 테이블 업데이트
function updateDevicesTable(devices) {
    const tbody = document.getElementById('devicesTableBody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    devices.forEach(device => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${device.device_name}</td>
            <td>${device.store_name || 'N/A'}</td>
            <td>${device.device_type}</td>
            <td><span class="badge badge-${getStatusClass(device.status)}">${getStatusText(device.status)}</span></td>
            <td>
                <span class="health-score ${getHealthClass(device.health_score)}">
                    ${(device.health_score || 0).toFixed(1)}%
                </span>
            </td>
            <td>${formatDate(device.last_maintenance)}</td>
            <td>
                <button class="btn btn-sm btn-primary me-1" onclick="editDevice('${device.device_id}')">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteDevice('${device.device_id}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// 분석 차트 업데이트
function updateAnalyticsCharts(analytics) {
    if (analytics.temperature && charts.temperature) {
        charts.temperature.data.labels = analytics.temperature.labels || [];
        charts.temperature.data.datasets[0].data = analytics.temperature.values || [];
        charts.temperature.update();
    }
    
    if (analytics.vibration && charts.vibration) {
        charts.vibration.data.labels = analytics.vibration.labels || [];
        charts.vibration.data.datasets[0].data = analytics.vibration.values || [];
        charts.vibration.update();
    }
    
    if (analytics.power && charts.power) {
        charts.power.data.labels = analytics.power.labels || [];
        charts.power.data.datasets[0].data = analytics.power.values || [];
        charts.power.update();
    }
    
    if (analytics.anomaly && charts.anomaly) {
        charts.anomaly.data.labels = analytics.anomaly.labels || [];
        charts.anomaly.data.datasets[0].data = analytics.anomaly.values || [];
        charts.anomaly.update();
    }
}

// 알림 테이블 업데이트
function updateNotificationsTable(notifications) {
    const tbody = document.getElementById('notificationsTableBody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    notifications.forEach(notification => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${formatDate(notification.created_at)}</td>
            <td><span class="badge badge-${getPriorityClass(notification.priority)}">${notification.event_type}</span></td>
            <td>${notification.store_name || 'N/A'}</td>
            <td>${notification.message}</td>
            <td><span class="badge badge-${getStatusClass(notification.status)}">${getStatusText(notification.status)}</span></td>
        `;
        tbody.appendChild(row);
    });
}

// 유틸리티 함수들
function getStatusClass(status) {
    const statusMap = {
        'active': 'success',
        'online': 'success',
        'inactive': 'secondary',
        'offline': 'danger',
        'maintenance': 'info',
        'warning': 'warning',
        'critical': 'danger',
        'sent': 'success',
        'delivered': 'success',
        'failed': 'danger',
        'pending': 'warning'
    };
    return statusMap[status] || 'secondary';
}

function getStatusText(status) {
    const statusMap = {
        'active': '활성',
        'online': '온라인',
        'inactive': '비활성',
        'offline': '오프라인',
        'maintenance': '점검중',
        'warning': '경고',
        'critical': '위험',
        'sent': '전송됨',
        'delivered': '전달됨',
        'failed': '실패',
        'pending': '대기중'
    };
    return statusMap[status] || status;
}

function getHealthClass(score) {
    if (score >= 80) return 'excellent';
    if (score >= 60) return 'good';
    if (score >= 40) return 'warning';
    return 'critical';
}

function getPriorityClass(priority) {
    const priorityMap = {
        'low': 'secondary',
        'medium': 'warning',
        'high': 'danger',
        'critical': 'danger'
    };
    return priorityMap[priority] || 'secondary';
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 이벤트 리스너 설정
function setupEventListeners() {
    // 알림 설정 폼
    const notificationForm = document.getElementById('notificationSettingsForm');
    if (notificationForm) {
        notificationForm.addEventListener('submit', function(e) {
            e.preventDefault();
            saveNotificationSettings();
        });
    }
    
    // 매장 추가 폼
    const addStoreForm = document.getElementById('addStoreForm');
    if (addStoreForm) {
        addStoreForm.addEventListener('submit', function(e) {
            e.preventDefault();
            addStore();
        });
    }
    
    // 디바이스 추가 폼
    const addDeviceForm = document.getElementById('addDeviceForm');
    if (addDeviceForm) {
        addDeviceForm.addEventListener('submit', function(e) {
            e.preventDefault();
            addDevice();
        });
    }
}

// 자동 새로고침 시작
function startAutoRefresh() {
    refreshInterval = setInterval(() => {
        if (currentSection === 'overview') {
            loadOverviewData();
        }
    }, 30000); // 30초마다 새로고침
}

// 자동 새로고침 중지
function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
}

// 알림 설정 저장
async function saveNotificationSettings() {
    try {
        const settings = {
            email_enabled: document.getElementById('emailEnabled').checked,
            sms_enabled: document.getElementById('smsEnabled').checked,
            quiet_hours_start: document.getElementById('quietStart').value,
            quiet_hours_end: document.getElementById('quietEnd').value,
            max_notifications_per_hour: parseInt(document.getElementById('maxNotifications').value)
        };
        
        const response = await fetch('/api/dashboard/notification-settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('알림 설정이 저장되었습니다.', 'success');
        } else {
            showAlert('알림 설정 저장에 실패했습니다.', 'danger');
        }
    } catch (error) {
        console.error('알림 설정 저장 실패:', error);
        showAlert('알림 설정 저장에 실패했습니다.', 'danger');
    }
}

// 매장 추가 모달 표시
function showAddStoreModal() {
    const modal = new bootstrap.Modal(document.getElementById('addStoreModal'));
    modal.show();
}

// 디바이스 추가 모달 표시
function showAddDeviceModal() {
    const modal = new bootstrap.Modal(document.getElementById('addDeviceModal'));
    modal.show();
    
    // 매장 목록 로드
    loadStoreOptions();
}

// 매장 옵션 로드
async function loadStoreOptions() {
    try {
        const response = await fetch('/api/dashboard/stores');
        const data = await response.json();
        
        if (data.success) {
            const select = document.getElementById('deviceStore');
            select.innerHTML = '<option value="">매장 선택</option>';
            
            data.stores.forEach(store => {
                const option = document.createElement('option');
                option.value = store.store_id;
                option.textContent = store.store_name;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('매장 목록 로드 실패:', error);
    }
}

// 매장 추가
async function addStore() {
    try {
        const storeData = {
            store_name: document.getElementById('storeName').value,
            store_type: document.getElementById('storeType').value,
            address: document.getElementById('storeAddress').value,
            city: document.getElementById('storeCity').value,
            state: document.getElementById('storeState').value,
            zip_code: document.getElementById('storeZipCode').value,
            phone: document.getElementById('storePhone').value,
            email: document.getElementById('storeEmail').value,
            owner_id: 'current_user' // 실제로는 현재 사용자 ID
        };
        
        const response = await fetch('/api/dashboard/stores', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(storeData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('매장이 추가되었습니다.', 'success');
            bootstrap.Modal.getInstance(document.getElementById('addStoreModal')).hide();
            loadStoresData();
        } else {
            showAlert('매장 추가에 실패했습니다.', 'danger');
        }
    } catch (error) {
        console.error('매장 추가 실패:', error);
        showAlert('매장 추가에 실패했습니다.', 'danger');
    }
}

// 디바이스 추가
async function addDevice() {
    try {
        const deviceData = {
            device_name: document.getElementById('deviceName').value,
            store_id: document.getElementById('deviceStore').value,
            device_type: document.getElementById('deviceType').value,
            model: document.getElementById('deviceModel').value,
            serial_number: document.getElementById('deviceSerial').value
        };
        
        const response = await fetch('/api/dashboard/devices', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(deviceData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('디바이스가 추가되었습니다.', 'success');
            bootstrap.Modal.getInstance(document.getElementById('addDeviceModal')).hide();
            loadDevicesData();
        } else {
            showAlert('디바이스 추가에 실패했습니다.', 'danger');
        }
    } catch (error) {
        console.error('디바이스 추가 실패:', error);
        showAlert('디바이스 추가에 실패했습니다.', 'danger');
    }
}

// 매장 편집
function editStore(storeId) {
    console.log('매장 편집:', storeId);
    // TODO: 매장 편집 기능 구현
}

// 매장 삭제
async function deleteStore(storeId) {
    if (confirm('정말로 이 매장을 삭제하시겠습니까?')) {
        try {
            const response = await fetch(`/api/dashboard/stores/${storeId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert('매장이 삭제되었습니다.', 'success');
                loadStoresData();
            } else {
                showAlert('매장 삭제에 실패했습니다.', 'danger');
            }
        } catch (error) {
            console.error('매장 삭제 실패:', error);
            showAlert('매장 삭제에 실패했습니다.', 'danger');
        }
    }
}

// 디바이스 편집
function editDevice(deviceId) {
    console.log('디바이스 편집:', deviceId);
    // TODO: 디바이스 편집 기능 구현
}

// 디바이스 삭제
async function deleteDevice(deviceId) {
    if (confirm('정말로 이 디바이스를 삭제하시겠습니까?')) {
        try {
            const response = await fetch(`/api/dashboard/devices/${deviceId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert('디바이스가 삭제되었습니다.', 'success');
                loadDevicesData();
            } else {
                showAlert('디바이스 삭제에 실패했습니다.', 'danger');
            }
        } catch (error) {
            console.error('디바이스 삭제 실패:', error);
            showAlert('디바이스 삭제에 실패했습니다.', 'danger');
        }
    }
}

// 차트 업데이트
function updateChart(period) {
    console.log('차트 업데이트:', period);
    // TODO: 차트 업데이트 기능 구현
}

// 알림 표시
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // 5초 후 자동 제거
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// 페이지 언로드 시 정리
window.addEventListener('beforeunload', function() {
    stopAutoRefresh();
});

// 에러 처리
window.addEventListener('error', function(e) {
    console.error('JavaScript 오류:', e.error);
    showAlert('예상치 못한 오류가 발생했습니다.', 'danger');
});

// 네트워크 오류 처리
window.addEventListener('online', function() {
    showAlert('인터넷 연결이 복구되었습니다.', 'success');
    loadDashboardData();
});

window.addEventListener('offline', function() {
    showAlert('인터넷 연결이 끊어졌습니다.', 'warning');
});
