// static/js/dashboard/dashboard.js
import { showAlert, startAutoRefreshHelper, stopAutoRefreshHelper, openModal, closeModal } 
         from '../../common/utils/helpers.js';
import { getStatusClass, getStatusText, getPriorityClass, getHealthClass, formatDate } 
         from '../../common/utils/formatters.js';

let chartManager;
let dataLoader;
let tableRenderer;
let sectionManager;
let cardUpdater;
let apiClient;
let refreshInterval;

document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
    loadDashboardData();
    setupEventListeners();
    startAutoRefresh();
});

function initializeDashboard() {
    console.log('대시보드 초기화 중...');

    // 인스턴스 생성
    apiClient = new DashboardApiClient();
    chartManager = new ChartManager();
    dataLoader = new DataLoader(apiClient);
    tableRenderer = new TableRenderer();
    sectionManager = new SectionManager();
    cardUpdater = new CardUpdater();

    // 의존성 주입
    sectionManager.setDependencies(tableRenderer, cardUpdater, dataLoader, chartManager);

    // 초기화
    chartManager.initializeAllCharts();
    sectionManager.setupNavigation();

    console.log('대시보드 초기화 완료');
}

async function loadDashboardData() {
    try {
        const data = await dataLoader.loadDashboardData();

        if (data.success) {
            cardUpdater.updateOverviewCards(data.summary);
            if (chartManager.charts.energy) chartManager.charts.energy.update(data.energy_data);
            if (chartManager.charts.deviceStatus) chartManager.charts.deviceStatus.update(data.device_status);
        }
    } catch (error) {
        console.error('대시보드 데이터 로드 실패:', error);
        showAlert('데이터 로드에 실패했습니다.', 'danger');
    }
}

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

function startAutoRefresh() {
    refreshInterval = startAutoRefreshHelper(() => {
        if (sectionManager.currentSection === 'overview') {
            sectionManager.loadOverviewData();
        }
    }, 30000); // 30초마다 새로고침
}

function stopAutoRefresh() {
    if (refreshInterval) {
        stopAutoRefreshHelper(refreshInterval);
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

        const data = await apiClient.saveNotificationSettings(settings);

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
    openModal('addStoreModal');
}

// 디바이스 추가 모달 표시
function showAddDeviceModal() {
    openModal('addDeviceModal');

    // 매장 목록 로드
    loadStoreOptions();
}

// 매장 옵션 로드
async function loadStoreOptions() {
    try {
        const data = await apiClient.fetchStores();

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

        const data = await apiClient.addStore(storeData);

        if (data.success) {
            showAlert('매장이 추가되었습니다.', 'success');
            closeModal('addStoreModal');
            sectionManager.loadStoresData();
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

        const data = await apiClient.addDevice(deviceData);

        if (data.success) {
            showAlert('디바이스가 추가되었습니다.', 'success');
            closeModal('addDeviceModal');
            sectionManager.loadDevicesData();
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
            const data = await apiClient.deleteStore(storeId);

            if (data.success) {
                showAlert('매장이 삭제되었습니다.', 'success');
                sectionManager.loadStoresData();
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
            const data = await apiClient.deleteDevice(deviceId);

            if (data.success) {
                showAlert('디바이스가 삭제되었습니다.', 'success');
                sectionManager.loadDevicesData();
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

// 전역 변수로 기존 함수들을 등록 (하위 호환성 유지)
window.showSection = (section) => sectionManager.showSection(section);
window.editStore = (storeId) => { /* ... */ };
window.deleteStore = (storeId) => { /* ... */ };
window.editDevice = (deviceId) => { /* ... */ };
window.deleteDevice = (deviceId) => { /* ... */ };

// 전역 함수로 유틸리티 함수 등록 (하위 호환성 유지)
window.showAlert = showAlert;
window.getStatusClass = getStatusClass;
window.getStatusText = getStatusText;
window.getHealthClass = getHealthClass;
window.getPriorityClass = getPriorityClass;
window.formatDate = formatDate;

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

// 전역 설정 초기화 함수
window.initializeSettingsPage = async function() {
    try {
        // 동적으로 설정 관련 JS 모듈 로드
        const { SettingsManager } = await import('/static/js/dashboard/settings/settings-main.js');
        const settingsManager = new SettingsManager();
        await settingsManager.initialize();
        
        // 전역으로 사용할 수 있도록 설정
        window.settingsManager = settingsManager;
        
        // 설정 저장 이벤트 연결
        const saveButton = document.querySelector('.settings-footer .btn-primary');
        if (saveButton) {
            saveButton.addEventListener('click', async function() {
                try {
                    await settingsManager.saveSettings();
                    showAlert('설정이 성공적으로 저장되었습니다.', 'success');
                } catch (error) {
                    console.error('설정 저장 오류:', error);
                    showAlert('설정 저장에 실패했습니다.', 'danger');
                }
            });
        }
    } catch (error) {
        console.error('설정 페이지 초기화 오류:', error);
    }
};