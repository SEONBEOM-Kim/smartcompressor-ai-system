// static/js/dashboard/settings/settings-main.js

import { SettingsApiClient } from './api.js';
import { initializeSettings } from './ui.js';

class SettingsManager {
    constructor() {
        this.apiClient = new SettingsApiClient();
        this.settings = {};
    }

    async initialize() {
        try {
            console.log('Initializing settings manager...');
            await this.loadSettings();
            initializeSettings();
            console.log('Settings manager initialized successfully.');
        } catch (error) {
            console.error('Error initializing settings manager:', error);
        }
    }

    async loadSettings() {
        try {
            console.log('Loading settings from API...');
            const data = await this.apiClient.fetchSettings();
            this.settings = data;
            this.renderSettings();
        } catch (error) {
            console.error('Failed to load settings:', error);
            // Use default settings if API call fails
            this.settings = this.getDefaultSettings();
            this.renderSettings();
        }
    }

    getDefaultSettings() {
        return {
            general: {
                companyName: 'SignalCraft',
                timezone: 'KST',
                language: 'ko',
                theme: 'light',
                autoRefresh: true,
                showAnomalyTrend: true,
                showAssetTrend: true
            },
            notifications: {
                emailEnabled: true,
                smsEnabled: false,
                pushEnabled: true,
                maxNotifications: 10,
                quietStart: '22:00',
                quietEnd: '08:00',
                alertCritical: true,
                alertWarning: true,
                alertOffline: false,
                alertMaintenance: true
            },
            security: {
                passwordMinLength: 8,
                requireTwoFactor: true,
                sessionTimeout: true,
                ipWhitelist: false,
                logUserActions: true,
                logFailedLogins: true,
                logRetention: 90
            },
            account: {
                name: '관리자',
                email: 'admin@signalcraft.com',
                role: '시스템 관리자'
            }
        };
    }

    renderSettings() {
        // Populate form fields with settings data
        this.populateGeneralSettings();
        this.populateNotificationSettings();
        this.populateSecuritySettings();
        this.populateAccountSettings();
    }

    populateGeneralSettings() {
        if (this.settings.general) {
            const general = this.settings.general;
            
            document.getElementById('companyName')?.setAttribute('value', general.companyName || '');
            document.getElementById('timezone')?.value = general.timezone || 'KST';
            document.getElementById('language')?.value = general.language || 'ko';
            document.getElementById('theme')?.value = general.theme || 'light';
            
            document.getElementById('autoRefresh')?.checked = general.autoRefresh !== false;
            document.getElementById('showAnomalyTrend')?.checked = general.showAnomalyTrend !== false;
            document.getElementById('showAssetTrend')?.checked = general.showAssetTrend !== false;
        }
    }

    populateNotificationSettings() {
        if (this.settings.notifications) {
            const notifications = this.settings.notifications;
            
            document.getElementById('emailEnabled')?.checked = notifications.emailEnabled !== false;
            document.getElementById('smsEnabled')?.checked = notifications.smsEnabled === true;
            document.getElementById('pushEnabled')?.checked = notifications.pushEnabled !== false;
            document.getElementById('maxNotifications')?.value = notifications.maxNotifications || 10;
            document.getElementById('quietStart')?.value = notifications.quietStart || '22:00';
            document.getElementById('quietEnd')?.value = notifications.quietEnd || '08:00';
            
            document.getElementById('alertCritical')?.checked = notifications.alertCritical !== false;
            document.getElementById('alertWarning')?.checked = notifications.alertWarning !== false;
            document.getElementById('alertOffline')?.checked = notifications.alertOffline === true;
            document.getElementById('alertMaintenance')?.checked = notifications.alertMaintenance !== false;
        }
    }

    populateSecuritySettings() {
        if (this.settings.security) {
            const security = this.settings.security;
            
            document.getElementById('passwordMinLength')?.value = security.passwordMinLength || 8;
            document.getElementById('requireTwoFactor')?.checked = security.requireTwoFactor !== false;
            document.getElementById('sessionTimeout')?.checked = security.sessionTimeout !== false;
            document.getElementById('ipWhitelist')?.checked = security.ipWhitelist === true;
            document.getElementById('logUserActions')?.checked = security.logUserActions !== false;
            document.getElementById('logFailedLogins')?.checked = security.logFailedLogins !== false;
            document.getElementById('logRetention')?.value = security.logRetention || 90;
        }
    }

    populateAccountSettings() {
        if (this.settings.account) {
            const account = this.settings.account;
            
            document.getElementById('accountName')?.setAttribute('value', account.name || '');
            document.getElementById('accountEmail')?.setAttribute('value', account.email || '');
            document.getElementById('accountRole')?.setAttribute('value', account.role || '');
        }
    }

    async saveSettings() {
        try {
            const settingsData = this.collectAllSettings();
            
            console.log('Saving settings to API...');
            const result = await this.apiClient.updateSettings(settingsData);
            
            console.log('Settings saved successfully:', result);
            
            // Update internal settings
            this.settings = { ...this.settings, ...settingsData };
            
            // Apply theme immediately after saving
            if (typeof window.applyTheme === 'function') {
                window.applyTheme();
            }
            
            return result;
        } catch (error) {
            console.error('Error saving settings:', error);
            throw error;
        }
    }

    collectAllSettings() {
        // Collect all settings from the form
        return {
            general: {
                companyName: document.getElementById('companyName')?.value,
                timezone: document.getElementById('timezone')?.value,
                language: document.getElementById('language')?.value,
                theme: document.getElementById('theme')?.value,
                autoRefresh: document.getElementById('autoRefresh')?.checked,
                showAnomalyTrend: document.getElementById('showAnomalyTrend')?.checked,
                showAssetTrend: document.getElementById('showAssetTrend')?.checked
            },
            notifications: {
                emailEnabled: document.getElementById('emailEnabled')?.checked,
                smsEnabled: document.getElementById('smsEnabled')?.checked,
                pushEnabled: document.getElementById('pushEnabled')?.checked,
                maxNotifications: document.getElementById('maxNotifications')?.value,
                quietStart: document.getElementById('quietStart')?.value,
                quietEnd: document.getElementById('quietEnd')?.value,
                alertCritical: document.getElementById('alertCritical')?.checked,
                alertWarning: document.getElementById('alertWarning')?.checked,
                alertOffline: document.getElementById('alertOffline')?.checked,
                alertMaintenance: document.getElementById('alertMaintenance')?.checked
            },
            security: {
                passwordMinLength: document.getElementById('passwordMinLength')?.value,
                requireTwoFactor: document.getElementById('requireTwoFactor')?.checked,
                sessionTimeout: document.getElementById('sessionTimeout')?.checked,
                ipWhitelist: document.getElementById('ipWhitelist')?.checked,
                logUserActions: document.getElementById('logUserActions')?.checked,
                logFailedLogins: document.getElementById('logFailedLogins')?.checked,
                logRetention: document.getElementById('logRetention')?.value
            }
        };
    }

    async updateAccountInfo() {
        try {
            const accountInfo = {
                name: document.getElementById('accountName')?.value,
                email: document.getElementById('accountEmail')?.value
            };

            const result = await this.apiClient.updateAccountInfo(accountInfo);
            
            console.log('Account info updated successfully:', result);
            
            // Update internal settings
            this.settings.account = { ...this.settings.account, ...accountInfo };
            
            return result;
        } catch (error) {
            console.error('Error updating account info:', error);
            throw error;
        }
    }

    async changePassword(passwordData) {
        try {
            const result = await this.apiClient.changePassword(passwordData);
            
            console.log('Password changed successfully:', result);
            
            return result;
        } catch (error) {
            console.error('Error changing password:', error);
            throw error;
        }
    }
}

// Export the SettingsManager class
export { SettingsManager };