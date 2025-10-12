// Import all modules
import PWAManager from './pwa/pwa-manager.js';
import NotificationHandler from './pwa/notification-handler.js';
import MobileApiClient from './data/api-client.js';
import DataLoader from './data/data-loader.js';
import OfflineStorage from './data/offline-storage.js';
import DashboardUpdater from './ui/dashboard-updater.js';
import PaymentRenderer from './ui/payment-renderer.js';
import NotificationRenderer from './ui/notification-renderer.js';
import NavigationManager from './ui/navigation-manager.js';
import MonitoringChart from './charts/monitoring-chart.js';
import { formatTime, hideLoadingScreen } from './utils/formatters.js';
import { handleOnlineStatus, animateDiagnosisProgress, showDiagnosisResult, showDiagnosisError } from './utils/helpers.js';

// Global variables for modules
window.pwaManager = null;
window.dataLoader = null;
window.dashboardUpdater = null;
window.paymentRenderer = null;
window.notificationRenderer = null;
window.navigationManager = null;
window.monitoringChart = null;
window.notificationHandler = null;
window.apiClient = null;
window.offlineStorage = null;

class TeslaMobileApp {
    constructor() {
        this.isOnline = navigator.onLine;
        this.currentSection = 'dashboard';
        this.notifications = [];
        this.paymentData = [];
        this.monitoringData = {
            temperature: [],
            efficiency: [],
            power: []
        };
        
        this.init();
    }

    async init() {
        console.log('🚀 Tesla Mobile App 초기화 시작');
        
        // 인스턴스 생성
        window.apiClient = new MobileApiClient();
        window.pwaManager = new PWAManager();
        window.dataLoader = new DataLoader(window.apiClient);
        window.offlineStorage = new OfflineStorage();
        window.dashboardUpdater = new DashboardUpdater();
        window.paymentRenderer = new PaymentRenderer();
        window.notificationRenderer = new NotificationRenderer();
        window.navigationManager = new NavigationManager();
        window.monitoringChart = new MonitoringChart('monitoringChart');
        window.notificationHandler = new NotificationHandler();
        
        // 초기화
        this.setupEventListeners();
        await window.pwaManager.init();
        await this.loadInitialData();
        hideLoadingScreen();
        window.monitoringChart.init(); // Initialize chart after data is loaded
        this.startRealTimeUpdates();
        
        console.log('✅ Tesla Mobile App 초기화 완료');
    }

    setupEventListeners() {
        // 네비게이션
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const section = e.currentTarget.dataset.section;
                window.navigationManager.navigateToSection(section);
            });
        });

        // 액션 버튼들
        document.getElementById('diagnoseBtn')?.addEventListener('click', () => {
            this.startDiagnosis();
        });

        document.getElementById('controlBtn')?.addEventListener('click', () => {
            this.showControlPanel();
        });

        // 모니터링 컨트롤
        document.querySelectorAll('.control-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                window.monitoringChart.switchMonitoringType(e.currentTarget.dataset.type);
            });
        });

        // 탭 전환
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                window.navigationManager.switchTab(e.currentTarget.dataset.tab);
            });
        });

        // 백 버튼들
        document.querySelectorAll('.back-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                window.navigationManager.navigateToSection('dashboard');
            });
        });

        // 온라인/오프라인 상태
        window.addEventListener('online', () => {
            handleOnlineStatus(true, (isOnline) => {
                this.isOnline = isOnline;
            });
        });

        window.addEventListener('offline', () => {
            handleOnlineStatus(false, (isOnline) => {
                this.isOnline = isOnline;
            });
        });

        // 푸시 알림 테스트
        document.getElementById('testDiagnosisNotification')?.addEventListener('click', () => {
            window.notificationHandler.testPushNotification('diagnosis');
        });

        document.getElementById('testPaymentNotification')?.addEventListener('click', () => {
            window.notificationHandler.testPushNotification('payment');
        });
    }

    async loadInitialData() {
        try {
            await this.loadDashboardData();
            await this.loadPaymentData();
            await this.loadNotificationData();
        } catch (error) {
            console.error('❌ 초기 데이터 로드 실패:', error);
            window.notificationHandler.showToast('데이터 로드에 실패했습니다', 'error');
        }
    }

    async loadDashboardData() {
        try {
            const data = await window.dataLoader.loadDashboardData();
            window.dashboardUpdater.updateDashboardUI(data);
        } catch (error) {
            console.error('대시보드 데이터 로드 실패:', error);
        }
    }

    async loadPaymentData() {
        try {
            const data = await window.dataLoader.loadPaymentData();
            this.paymentData = data.payments || [];
            window.paymentRenderer.updatePaymentList(this.paymentData);
        } catch (error) {
            console.error('결제 데이터 로드 실패:', error);
        }
    }

    async loadNotificationData() {
        try {
            const data = await window.dataLoader.loadNotificationData();
            this.notifications = data.notifications || [];
            window.notificationRenderer.updateNotificationBadge(this.notifications);
            window.notificationRenderer.updateNotificationHistory(this.notifications);
        } catch (error) {
            console.error('알림 데이터 로드 실패:', error);
        }
    }

    startRealTimeUpdates() {
        // 주기적 대시보드 및 알림 업데이트
        setInterval(() => {
            if (this.isOnline) {
                this.loadDashboardData();
                this.loadNotificationData();
            }
        }, 5000);

        // 주기적 모니터링 데이터 업데이트
        setInterval(() => {
            window.monitoringChart.updateMonitoringData();
        }, 1000);
    }

    async startDiagnosis() {
        console.log('🔍 진단 시작');
        
        window.navigationManager.navigateToSection('diagnosis');
        animateDiagnosisProgress();
        
        try {
            const result = await window.apiClient.startDiagnosis('store_001');
            showDiagnosisResult(result);
        } catch (error) {
            console.error('진단 오류:', error);
            showDiagnosisError(window.notificationHandler.showToast.bind(window.notificationHandler));
        }
    }

    showControlPanel() {
        // Placeholder for control panel functionality
        console.log('컨트롤 패널 열기');
    }
}

// 앱 초기화
document.addEventListener('DOMContentLoaded', () => {
    window.teslaApp = new TeslaMobileApp();
});

// PWA 설치 이벤트 (already handled in pwa-manager.js)