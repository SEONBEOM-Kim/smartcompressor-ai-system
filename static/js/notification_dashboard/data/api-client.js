/**
 * API Client for Notification Dashboard
 * Handles all API calls for the notification management system
 */

class NotificationApiClient {
    constructor() {
        this.baseUrl = '/api/notifications';
    }

    /**
     * Fetch notification status data
     */
    async fetchStatus() {
        try {
            const response = await fetch(`${this.baseUrl}/status`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching status:', error);
            throw error;
        }
    }

    /**
     * Fetch notification channels data
     */
    async fetchChannels() {
        try {
            const response = await fetch(`${this.baseUrl}/channels`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching channels:', error);
            throw error;
        }
    }

    /**
     * Fetch notification history
     * @param {number} limit - Number of records to fetch (default: 10)
     */
    async fetchHistory(limit = 10) {
        try {
            const response = await fetch(`${this.baseUrl}/history?limit=${limit}`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching history:', error);
            throw error;
        }
    }

    /**
     * Fetch filtered notification history
     * @param {Object} filters - Filter parameters
     */
    async fetchFilteredHistory(filters = {}) {
        try {
            let url = `${this.baseUrl}/history?limit=50`;
            if (filters.type) url += `&type=${filters.type}`;
            if (filters.channel) url += `&channel=${filters.channel}`;
            if (filters.date) url += `&date=${filters.date}`;

            const response = await fetch(url);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching filtered history:', error);
            throw error;
        }
    }

    /**
     * Fetch notification templates
     */
    async fetchTemplates() {
        try {
            const response = await fetch(`${this.baseUrl}/email/templates`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error fetching templates:', error);
            throw error;
        }
    }

    /**
     * Send a quick notification
     * @param {Object} notificationData - Notification data to send
     */
    async sendNotification(notificationData) {
        try {
            const response = await fetch(`${this.baseUrl}/send`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(notificationData)
            });
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error sending notification:', error);
            throw error;
        }
    }

    /**
     * Test a notification channel
     * @param {string} channelName - Name of the channel to test
     */
    async testChannel(channelName) {
        try {
            const response = await fetch(`${this.baseUrl}/test/${channelName}`, {
                method: 'POST'
            });
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error testing channel:', error);
            throw error;
        }
    }

    /**
     * Create a new notification template
     * @param {Object} templateData - Template data to create
     */
    async createTemplate(templateData) {
        try {
            const response = await fetch(`${this.baseUrl}/email/templates`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(templateData)
            });
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error creating template:', error);
            throw error;
        }
    }

    /**
     * Update an existing notification template
     * @param {string} templateId - ID of the template to update
     * @param {Object} templateData - Updated template data
     */
    async updateTemplate(templateId, templateData) {
        try {
            const response = await fetch(`${this.baseUrl}/email/templates/${templateId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(templateData)
            });
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error updating template:', error);
            throw error;
        }
    }

    /**
     * Delete a notification template
     * @param {string} templateId - ID of the template to delete
     */
    async deleteTemplate(templateId) {
        try {
            const response = await fetch(`${this.baseUrl}/email/templates/${templateId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Error deleting template:', error);
            throw error;
        }
    }
}

// Export the class for use in other modules
export default NotificationApiClient;