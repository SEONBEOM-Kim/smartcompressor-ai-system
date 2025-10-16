// static/js/dashboard/data/data-loader.js
class DataLoader {
    constructor(apiClient) {
        this.apiClient = apiClient;
    }

    async loadOverviewData() {
        try {
            const data = await this.apiClient.fetchSummary();
            return data;
        } catch (error) {
            console.error('개요 데이터 로드 실패:', error);
            throw error;
        }
    }

    async loadStoresData() {
        try {
            const data = await this.apiClient.fetchStores();
            return data;
        } catch (error) {
            console.error('매장 데이터 로드 실패:', error);
            throw error;
        }
    }

    async loadDevicesData() {
        try {
            const data = await this.apiClient.fetchDevices();
            return data;
        } catch (error) {
            console.error('디바이스 데이터 로드 실패:', error);
            throw error;
        }
    }

    async loadAnalyticsData() {
        try {
            const data = await this.apiClient.fetchAnalytics();
            return data;
        } catch (error) {
            console.error('분석 데이터 로드 실패:', error);
            throw error;
        }
    }

    async loadNotificationsData() {
        try {
            const data = await this.apiClient.fetchNotifications();
            return data;
        } catch (error) {
            console.error('알림 데이터 로드 실패:', error);
            throw error;
        }
    }

    async loadDashboardData() {
        try {
            const data = await this.apiClient.fetchSummary();
            return data;
        } catch (error) {
            console.error('대시보드 데이터 로드 실패:', error);
            throw error;
        }
    }
}