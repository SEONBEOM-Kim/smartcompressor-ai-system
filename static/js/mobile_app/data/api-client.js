class MobileApiClient {
    constructor(baseUrl = '/api') {
        this.baseUrl = baseUrl;
    }

    async fetchDashboardSummary() {
        try {
            const response = await fetch(`${this.baseUrl}/dashboard/summary`);
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Dashboard summary fetch failed with status ${response.status}`);
            }
        } catch (error) {
            console.error('대시보드 데이터 로드 실패:', error);
            throw error;
        }
    }

    async fetchPayments() {
        try {
            const response = await fetch(`${this.baseUrl}/mobile_app/payments`);
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Payments fetch failed with status ${response.status}`);
            }
        } catch (error) {
            console.error('결제 데이터 로드 실패:', error);
            throw error;
        }
    }

    async fetchNotifications() {
        try {
            const response = await fetch(`${this.baseUrl}/notifications/history`);
            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Notifications fetch failed with status ${response.status}`);
            }
        } catch (error) {
            console.error('알림 데이터 로드 실패:', error);
            throw error;
        }
    }

    async startDiagnosis(storeId) {
        try {
            const response = await fetch(`${this.baseUrl}/ai/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    store_id: storeId || 'store_001',
                    analysis_type: 'compressor_door_status'
                })
            });

            if (response.ok) {
                return await response.json();
            } else {
                throw new Error(`Diagnosis failed with status ${response.status}`);
            }
        } catch (error) {
            console.error('진단 오류:', error);
            throw error;
        }
    }
}

export default MobileApiClient;