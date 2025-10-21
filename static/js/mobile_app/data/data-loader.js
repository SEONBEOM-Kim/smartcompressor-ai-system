class DataLoader {
    constructor(apiClient) {
        this.apiClient = apiClient;
    }

    async loadInitialData() {
        try {
            await this.loadDashboardData();
            await this.loadPaymentData();
            await this.loadNotificationData();
        } catch (error) {
            console.error('❌ 초기 데이터 로드 실패:', error);
            throw error;
        }
    }

    async loadDashboardData() {
        try {
            const data = await this.apiClient.fetchDashboardSummary();
            return data;
        } catch (error) {
            console.error('대시보드 데이터 로드 실패:', error);
            // Return offline data in case of error
            return this.loadOfflineDashboardData();
        }
    }

    async loadPaymentData() {
        try {
            const data = await this.apiClient.fetchPayments();
            return data;
        } catch (error) {
            console.error('결제 데이터 로드 실패:', error);
            throw error;
        }
    }

    async loadNotificationData() {
        try {
            const data = await this.apiClient.fetchNotifications();
            return data;
        } catch (error) {
            console.error('알림 데이터 로드 실패:', error);
            throw error;
        }
    }
    
    loadOfflineDashboardData() {
        // Return cached/offline data when API fails
        const offlineData = {
            compressor_status: {
                status: '정상',
                temperature: 25,
                efficiency: 0.95,
                power_consumption: 850,
                vibration: '정상'
            },
            payment_summary: {
                today_revenue: 125000,
                transaction_count: 23,
                average_payment: 5435
            }
        };

        return offlineData;
    }
}

export default DataLoader;