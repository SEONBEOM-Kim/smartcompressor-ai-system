static/js/dashboard.js 모듈화를 위한 구체적인 플랜을 제시하겠습니다. 이 파일은 약 847줄의 코드를 포함하고 있으며 dashboard.js:1-14 , 다음과 같은 주요 기능들로 구성되어 있습니다.

현재 dashboard.js의 구조 분석
주요 기능 영역
차트 관리 (약 230줄): 6개의 Chart.js 차트 초기화 및 업데이트 dashboard.js:79-256
데이터 로딩 (약 90줄): API 호출 및 데이터 페칭 dashboard.js:258-343
테이블 렌더링 (약 150줄): 매장, 디바이스, 알림 테이블 업데이트 dashboard.js:377-409
섹션 관리 (약 80줄): 탭 전환 및 네비게이션 dashboard.js:36-77
유틸리티 함수 (약 100줄): 날짜 포맷, 상태 변환 등 dashboard.js:526-554
Phase 1: 폴더 구조 생성
static/js/dashboard/  
  ├── charts/  
  │   ├── chart-manager.js (새로 생성)  
  │   ├── energy-chart.js (새로 생성)  
  │   ├── device-status-chart.js (새로 생성)  
  │   ├── temperature-chart.js (새로 생성)  
  │   ├── vibration-chart.js (새로 생성)  
  │   ├── power-chart.js (새로 생성)  
  │   └── anomaly-chart.js (새로 생성)  
  ├── data/  
  │   ├── data-loader.js (새로 생성)  
  │   └── api-client.js (새로 생성)  
  ├── ui/  
  │   ├── table-renderer.js (새로 생성)  
  │   ├── section-manager.js (새로 생성)  
  │   └── card-updater.js (새로 생성)  
  ├── utils/  
  │   ├── formatters.js (새로 생성)  
  │   └── helpers.js (새로 생성)  
  └── dashboard.js (진입점만 유지)  
Phase 2: 차트 모듈 분리 (우선순위 1)
2.1 차트 매니저 생성
static/js/dashboard/charts/chart-manager.js

// static/js/dashboard/charts/chart-manager.js  
class ChartManager {  
    constructor() {  
        this.charts = {};  
    }  
  
    initializeAllCharts() {  
        this.initializeEnergyChart();  
        this.initializeDeviceStatusChart();  
        this.initializeTemperatureChart();  
        this.initializeVibrationChart();  
        this.initializePowerChart();  
        this.initializeAnomalyChart();  
    }  
  
    initializeEnergyChart() {  
        // static/js/dashboard.js:82-120의 로직 이동  
    }  
  
    initializeDeviceStatusChart() {  
        // static/js/dashboard.js:123-145의 로직 이동  
    }  
  
    // ... 나머지 차트 초기화 메서드  
}
2.2 개별 차트 클래스 분리
각 차트를 독립된 클래스로 분리:

static/js/dashboard/charts/energy-chart.js

class EnergyChart {  
    constructor(canvasId) {  
        this.canvas = document.getElementById(canvasId);  
        this.chart = null;  
        this.init();  
    }  
  
    init() {  
        // Chart.js 초기화 로직  
    }  
  
    update(data) {  
        if (this.chart && data) {  
            this.chart.data.labels = data.labels || [];  
            this.chart.data.datasets[0].data = data.values || [];  
            this.chart.update();  
        }  
    }  
}
Phase 3: 데이터 로딩 모듈 분리 (우선순위 2)
3.1 API 클라이언트 생성
static/js/dashboard/data/api-client.js

class DashboardApiClient {  
    constructor(baseUrl = '/api/dashboard') {  
        this.baseUrl = baseUrl;  
    }  
  
    async fetchSummary() {  
        // static/js/dashboard.js:259-273의 로직 이동  
        const response = await fetch(`${this.baseUrl}/summary`);  
        return response.json();  
    }  
  
    async fetchStores() {  
        // static/js/dashboard.js:290-301의 로직 이동  
    }  
  
    async fetchDevices() {  
        // static/js/dashboard.js:304-315의 로직 이동  
    }  
  
    async fetchAnalytics() {  
        // static/js/dashboard.js:318-329의 로직 이동  
    }  
  
    async fetchNotifications() {  
        // static/js/dashboard.js:332-343의 로직 이동  
    }  
}
3.2 데이터 로더 생성
static/js/dashboard/data/data-loader.js

class DataLoader {  
    constructor(apiClient) {  
        this.apiClient = apiClient;  
    }  
  
    async loadOverviewData() {  
        // static/js/dashboard.js:276-287의 로직 이동  
    }  
  
    async loadStoresData() {  
        // static/js/dashboard.js:290-301의 로직 이동  
    }  
  
    // ... 나머지 데이터 로딩 메서드  
}
Phase 4: UI 렌더링 모듈 분리 (우선순위 3)
4.1 테이블 렌더러 생성
static/js/dashboard/ui/table-renderer.js

class TableRenderer {  
    updateStoresTable(stores) {  
        // static/js/dashboard.js:378-409의 로직 이동  
    }  
  
    updateDevicesTable(devices) {  
        // static/js/dashboard.js:412-443의 로직 이동  
    }  
  
    updateNotificationsTable(notifications) {  
        // static/js/dashboard.js:472-489의 로직 이동  
    }  
}
4.2 섹션 매니저 생성
static/js/dashboard/ui/section-manager.js

class SectionManager {  
    constructor() {  
        this.currentSection = 'overview';  
    }  
  
    showSection(sectionName) {  
        // static/js/dashboard.js:36-77의 로직 이동  
    }  
  
    setupNavigation() {  
        // 네비게이션 이벤트 리스너 설정  
    }  
}
4.3 카드 업데이터 생성
static/js/dashboard/ui/card-updater.js

class CardUpdater {  
    updateOverviewCards(summary) {  
        // static/js/dashboard.js:346-353의 로직 이동  
    }  
}
Phase 5: 유틸리티 함수 분리 (우선순위 4)
5.1 포맷터 생성
static/js/dashboard/utils/formatters.js

// 날짜 포맷팅  
function formatDate(dateString) {  
    // static/js/dashboard.js:543-554의 로직 이동  
}  
  
// 상태 텍스트 변환  
function getStatusText(status) {  
    // static/js/dashboard.js:492-503의 로직 이동  
}  
  
// 상태 클래스 변환  
function getStatusClass(status) {  
    // static/js/dashboard.js:505-516의 로직 이동  
}  
  
// 우선순위 클래스 변환  
function getPriorityClass(priority) {  
    // static/js/dashboard.js:533-541의 로직 이동  
}  
  
// 헬스 스코어 클래스 변환  
function getHealthClass(score) {  
    // static/js/dashboard.js:526-531의 로직 이동  
}
Phase 6: 새로운 dashboard.js 구조
static/js/dashboard/dashboard.js (진입점만 유지)

// static/js/dashboard/dashboard.js  
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
      
    // 초기화  
    chartManager.initializeAllCharts();  
    sectionManager.setupNavigation();  
      
    console.log('대시보드 초기화 완료');  
}  
  
async function loadDashboardData() {  
    try {  
        const data = await apiClient.fetchSummary();  
          
        if (data.success) {  
            cardUpdater.updateOverviewCards(data.summary);  
            chartManager.charts.energy.update(data.energy_data);  
            chartManager.charts.deviceStatus.update(data.device_status);  
        }  
    } catch (error) {  
        console.error('대시보드 데이터 로드 실패:', error);  
        showAlert('데이터 로드에 실패했습니다.', 'danger');  
    }  
}  
  
// 전역 함수로 등록 (기존 호환성 유지)  
window.showSection = (section) => sectionManager.showSection(section);  
window.editStore = (storeId) => { /* ... */ };  
window.deleteStore = (storeId) => { /* ... */ };  
window.editDevice = (deviceId) => { /* ... */ };  
window.deleteDevice = (deviceId) => { /* ... */ };
Phase 7: HTML 파일 업데이트
templates/dashboard.html 스크립트 로드 순서 변경 dashboard.html:581-584 :

<!-- 기존 -->  
<script src="/static/js/dashboard.js"></script>  
  
<!-- 모듈화 후 -->  
<script src="/static/js/dashboard/utils/formatters.js"></script>  
<script src="/static/js/dashboard/charts/chart-manager.js"></script>  
<script src="/static/js/dashboard/data/api-client.js"></script>  
<script src="/static/js/dashboard/data/data-loader.js"></script>  
<script src="/static/js/dashboard/ui/table-renderer.js"></script>  
<script src="/static/js/dashboard/ui/section-manager.js"></script>  
<script src="/static/js/dashboard/ui/card-updater.js"></script>  
<script src="/static/js/dashboard/dashboard.js"></script>
실행 단계
Step 1: 차트 모듈 분리 (3-4일)
static/js/dashboard/charts/ 폴더 생성
chart-manager.js 및 개별 차트 클래스 생성
차트 초기화 및 업데이트 로직 이동
테스트: 모든 차트 정상 렌더링 확인
Step 2: 데이터 로딩 모듈 분리 (2-3일)
static/js/dashboard/data/ 폴더 생성
api-client.js, data-loader.js 생성
API 호출 로직 이동
테스트: 데이터 페칭 및 표시 정상 작동 확인
Step 3: UI 렌더링 모듈 분리 (2-3일)
static/js/dashboard/ui/ 폴더 생성
table-renderer.js, section-manager.js, card-updater.js 생성
UI 업데이트 로직 이동
테스트: 테이블, 섹션 전환, 카드 업데이트 정상 작동 확인
Step 4: 유틸리티 함수 분리 (1일)
static/js/dashboard/utils/ 폴더 생성
formatters.js, helpers.js 생성
공통 함수 이동
테스트: 날짜 포맷, 상태 변환 정상 작동 확인
Step 5: dashboard.js 간소화 (1일)
진입점 로직만 남기고 나머지 제거
전역 함수 등록 유지 (기존 호환성)
전체 대시보드 테스트
Step 6: HTML 업데이트 및 최종 검증 (1일)
templates/dashboard.html 스크립트 로드 순서 업데이트
전체 기능 테스트
배포 파이프라인 테스트
체크리스트
 static/js/dashboard/charts/chart-manager.js 생성 및 테스트
 개별 차트 클래스 생성 (6개)
 `static/