// static/js/dashboard/settings/api.js

export class SettingsApiClient {
    constructor() {
        this.baseURL = '/api/settings';
    }

    async fetchSettings() {
        try {
            const response = await fetch(`${this.baseURL}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    // In a real implementation, you'd include authentication headers
                    // 'Authorization': `Bearer ${getAuthToken()}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching settings:', error);
            throw error;
        }
    }

    async updateSettings(settings) {
        try {
            const response = await fetch(`${this.baseURL}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // In a real implementation, you'd include authentication headers
                    // 'Authorization': `Bearer ${getAuthToken()}`
                },
                body: JSON.stringify(settings)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error updating settings:', error);
            throw error;
        }
    }

    async updateAccountInfo(accountInfo) {
        try {
            const response = await fetch(`${this.baseURL}/account`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    // In a real implementation, you'd include authentication headers
                    // 'Authorization': `Bearer ${getAuthToken()}`
                },
                body: JSON.stringify(accountInfo)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error updating account info:', error);
            throw error;
        }
    }

    async changePassword(passwordData) {
        try {
            const response = await fetch(`${this.baseURL}/password`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    // In a real implementation, you'd include authentication headers
                    // 'Authorization': `Bearer ${getAuthToken()}`
                },
                body: JSON.stringify(passwordData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error changing password:', error);
            throw error;
        }
    }
}