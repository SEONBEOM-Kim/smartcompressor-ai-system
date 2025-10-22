// static/js/dashboard/settings/utils.js

// Utility functions for settings management

// Function to save settings to localStorage (fallback if API is not available)
export function saveSettingsToLocalStorage(settings) {
    try {
        localStorage.setItem('signalcraft_settings', JSON.stringify(settings));
        return true;
    } catch (error) {
        console.error('Error saving settings to localStorage:', error);
        return false;
    }
}

// Function to load settings from localStorage (fallback if API is not available)
export function loadSettingsFromLocalStorage() {
    try {
        const settingsStr = localStorage.getItem('signalcraft_settings');
        return settingsStr ? JSON.parse(settingsStr) : null;
    } catch (error) {
        console.error('Error loading settings from localStorage:', error);
        return null;
    }
}

// Function to validate settings before saving
export function validateSettings(settings) {
    const errors = [];
    
    // Validate company name
    if (!settings.general.companyName || settings.general.companyName.trim().length === 0) {
        errors.push('회사명을 입력해주세요.');
    }
    
    // Validate password length
    if (settings.security.passwordMinLength < 6) {
        errors.push('비밀번호 최소 길이는 6자 이상이어야 합니다.');
    }
    
    // Validate email format if provided
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (settings.account.email && !emailRegex.test(settings.account.email)) {
        errors.push('유효한 이메일 주소를 입력해주세요.');
    }
    
    // Validate quiet hours
    if (settings.notifications.quietStart && settings.notifications.quietEnd) {
        const start = new Date(`1970-01-01T${settings.notifications.quietStart}`);
        const end = new Date(`1970-01-01T${settings.notifications.quietEnd}`);
        
        if (start >= end) {
            errors.push('무음 시작 시간은 종료 시간보다 빨라야 합니다.');
        }
    }
    
    return {
        isValid: errors.length === 0,
        errors
    };
}

// Function to show alert using global showAlert if available
export function showSettingsAlert(message, type = 'info') {
    if (window.showAlert) {
        window.showAlert(message, type);
    } else {
        // Fallback to console or browser alert
        console[type === 'error' ? 'error' : type === 'warning' ? 'warn' : 'log'](message);
        alert(message);
    }
}

// Function to debounce save operations
export function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}