// static/js/dashboard/data/api-client.js
class DashboardApiClient {
    constructor(baseUrl = '/api/dashboard') {
        this.baseUrl = baseUrl;
    }

    async fetchSummary() {
        const response = await fetch(`${this.baseUrl}/summary`);
        return response.json();
    }

    async fetchStores() {
        const response = await fetch(`${this.baseUrl}/stores`);
        return response.json();
    }

    async fetchDevices() {
        const response = await fetch(`${this.baseUrl}/devices`);
        return response.json();
    }

    async fetchAnalytics() {
        const response = await fetch(`${this.baseUrl}/analytics`);
        return response.json();
    }

    async fetchNotifications() {
        const response = await fetch(`${this.baseUrl}/notifications`);
        return response.json();
    }

    async saveNotificationSettings(settings) {
        const response = await fetch(`${this.baseUrl}/notification-settings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });
        return response.json();
    }

    async addStore(storeData) {
        const response = await fetch(`${this.baseUrl}/stores`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(storeData)
        });
        return response.json();
    }

    async addDevice(deviceData) {
        const response = await fetch(`${this.baseUrl}/devices`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(deviceData)
        });
        return response.json();
    }

    async deleteStore(storeId) {
        const response = await fetch(`${this.baseUrl}/stores/${storeId}`, {
            method: 'DELETE'
        });
        return response.json();
    }

    async deleteDevice(deviceId) {
        const response = await fetch(`${this.baseUrl}/devices/${deviceId}`, {
            method: 'DELETE'
        });
        return response.json();
    }
}