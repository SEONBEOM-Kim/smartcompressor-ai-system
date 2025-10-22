// static/js/dashboard/settings/ui.js
import { showSettingsAlert, validateSettings, debounce } from './utils.js';

export function initializeSettings() {
    setupFormEventListeners();
    loadSettingsData();
}

function setupFormEventListeners() {
    // Save button - look for it in the settings actions card
    const saveButton = document.querySelector('.settings-actions .btn-primary');
    if (saveButton) {
        saveButton.addEventListener('click', saveSettings);
    }
    
    // Cancel button - look for it in the settings actions card
    const cancelButton = document.querySelector('.settings-actions .btn-secondary');
    if (cancelButton) {
        cancelButton.addEventListener('click', cancelSettings);
    }
    
    // Add real-time validation for important fields
    setupRealTimeValidation();
}

function setupRealTimeValidation() {
    // Password confirmation validation
    const newPasswordField = document.getElementById('newPassword');
    const confirmPasswordField = document.getElementById('confirmPassword');
    
    if (newPasswordField && confirmPasswordField) {
        const validatePasswordMatch = () => {
            if (newPasswordField.value !== confirmPasswordField.value) {
                confirmPasswordField.setCustomValidity('비밀번호가 일치하지 않습니다.');
            } else {
                confirmPasswordField.setCustomValidity('');
            }
        };
        
        newPasswordField.addEventListener('input', validatePasswordMatch);
        confirmPasswordField.addEventListener('input', validatePasswordMatch);
    }
    
    // Email validation
    document.querySelectorAll('input[type="email"]').forEach(input => {
        input.addEventListener('input', function() {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (this.value && !emailRegex.test(this.value)) {
                this.setCustomValidity('유효한 이메일 주소를 입력해주세요.');
            } else {
                this.setCustomValidity('');
            }
        });
    });
}

async function loadSettingsData() {
    try {
        console.log('Loading settings data...');
        
        // Try to load from localStorage first
        if (typeof window.loadSettingsFromLocalStorage === 'function') {
            const settings = window.loadSettingsFromLocalStorage();
            if (settings) {
                populateSettingsForm(settings);
                console.log('Settings loaded from localStorage.');
                return;
            }
        } else {
            // Use fallback utility
            const { loadSettingsFromLocalStorage } = await import('./utils.js');
            const settings = loadSettingsFromLocalStorage();
            if (settings) {
                populateSettingsForm(settings);
                console.log('Settings loaded from localStorage.');
                return;
            }
        }
        
        // If no settings in localStorage, use default values
        console.log('Using default settings.');
    } catch (error) {
        console.error('Error loading settings data:', error);
    }
}

function populateSettingsForm(settings) {
    if (settings.general) {
        const general = settings.general;
        document.getElementById('companyName')?.setAttribute('value', general.companyName || '');
        document.getElementById('timezone')?.value = general.timezone || 'KST';
        document.getElementById('language')?.value = general.language || 'ko';
        document.getElementById('theme')?.value = general.theme || 'light';
        
        document.getElementById('autoRefresh')?.checked = general.autoRefresh !== false;
        document.getElementById('showAnomalyTrend')?.checked = general.showAnomalyTrend !== false;
        document.getElementById('showAssetTrend')?.checked = general.showAssetTrend !== false;
    }
    
    if (settings.notifications) {
        const notifications = settings.notifications;
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
    
    if (settings.security) {
        const security = settings.security;
        document.getElementById('passwordMinLength')?.value = security.passwordMinLength || 8;
        document.getElementById('requireTwoFactor')?.checked = security.requireTwoFactor !== false;
        document.getElementById('sessionTimeout')?.checked = security.sessionTimeout !== false;
        document.getElementById('ipWhitelist')?.checked = security.ipWhitelist === true;
        document.getElementById('logUserActions')?.checked = security.logUserActions !== false;
        document.getElementById('logFailedLogins')?.checked = security.logFailedLogins !== false;
        document.getElementById('logRetention')?.value = security.logRetention || 90;
    }
    
    if (settings.account) {
        const account = settings.account;
        document.getElementById('accountName')?.setAttribute('value', account.name || '');
        document.getElementById('accountEmail')?.setAttribute('value', account.email || '');
        document.getElementById('accountRole')?.setAttribute('value', account.role || '');
    }
}

async function saveSettings() {
    try {
        // Collect all form data
        const settingsData = collectSettingsData();
        
        // Validate settings
        const validation = validateSettings(settingsData);
        if (!validation.isValid) {
            validation.errors.forEach(error => {
                showSettingsAlert(error, 'error');
            });
            return;
        }
        
        // In a real implementation, this would send data to the backend
        console.log('Saving settings:', settingsData);
        
        // Save to localStorage as fallback
        if (typeof window.saveSettingsToLocalStorage === 'function') {
            window.saveSettingsToLocalStorage(settingsData);
        } else {
            // Use fallback utility
            const { saveSettingsToLocalStorage } = await import('./utils.js');
            saveSettingsToLocalStorage(settingsData);
        }
        
        // Show success message
        showSettingsAlert('설정이 성공적으로 저장되었습니다.', 'success');
        console.log('Settings saved successfully.');
    } catch (error) {
        console.error('Error saving settings:', error);
        showSettingsAlert('설정 저장에 실패했습니다.', 'danger');
    }
}

function collectSettingsData() {
    // General settings
    const generalSettings = {
        companyName: document.getElementById('companyName')?.value,
        timezone: document.getElementById('timezone')?.value,
        language: document.getElementById('language')?.value,
        theme: document.getElementById('theme')?.value,
        autoRefresh: document.getElementById('autoRefresh')?.checked,
        showAnomalyTrend: document.getElementById('showAnomalyTrend')?.checked,
        showAssetTrend: document.getElementById('showAssetTrend')?.checked
    };
    
    // Notification settings
    const notificationSettings = {
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
    };
    
    // Security settings
    const securitySettings = {
        passwordMinLength: document.getElementById('passwordMinLength')?.value,
        requireTwoFactor: document.getElementById('requireTwoFactor')?.checked,
        sessionTimeout: document.getElementById('sessionTimeout')?.checked,
        ipWhitelist: document.getElementById('ipWhitelist')?.checked,
        logUserActions: document.getElementById('logUserActions')?.checked,
        logFailedLogins: document.getElementById('logFailedLogins')?.checked,
        logRetention: document.getElementById('logRetention')?.value
    };
    
    // Account settings
    const accountSettings = {
        name: document.getElementById('accountName')?.value,
        email: document.getElementById('accountEmail')?.value,
        newPassword: document.getElementById('newPassword')?.value,
        confirmPassword: document.getElementById('confirmPassword')?.value
    };
    
    return {
        general: generalSettings,
        notifications: notificationSettings,
        security: securitySettings,
        account: accountSettings
    };
}

function cancelSettings() {
    // Reset any changes by reloading the settings
    loadSettingsData();
    
    // Show message
    showSettingsAlert('변경 사항이 취소되었습니다.', 'info');
}

// Expose utility functions globally if needed
if (typeof window !== 'undefined') {
    window.showSettingsAlert = showSettingsAlert;
}