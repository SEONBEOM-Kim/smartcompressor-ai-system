class OfflineStorage {
    constructor() {
        this.storageKey = 'mobile_app_data';
    }
    
    loadOfflineDashboardData() {
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

    saveToCache(key, data) {
        try {
            const storage = window.localStorage;
            storage.setItem(`${this.storageKey}_${key}`, JSON.stringify(data));
        } catch (error) {
            console.error('Failed to save to cache:', error);
        }
    }

    loadFromCache(key) {
        try {
            const storage = window.localStorage;
            const cachedData = storage.getItem(`${this.storageKey}_${key}`);
            return cachedData ? JSON.parse(cachedData) : null;
        } catch (error) {
            console.error('Failed to load from cache:', error);
            return null;
        }
    }

    clearCache(key) {
        try {
            const storage = window.localStorage;
            storage.removeItem(`${this.storageKey}_${key}`);
        } catch (error) {
            console.error('Failed to clear cache:', error);
        }
    }
}

export default OfflineStorage;