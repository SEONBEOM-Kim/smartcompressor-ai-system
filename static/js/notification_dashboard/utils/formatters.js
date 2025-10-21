/**
 * Formatters for Notification Dashboard
 * Contains utility functions for formatting data
 */
import { formatDateTime as commonFormatDateTime } from '../../../common/utils/formatters.js';

// Export the common formatDateTime function
export { commonFormatDateTime as formatDateTime };

/**
 * Get the appropriate icon for a channel
 * @param {string} channelName - Name of the channel
 * @returns {string} Icon class name
 */
export function getChannelIcon(channelName) {
    const icons = {
        'websocket': 'wifi',
        'email': 'envelope',
        'kakao': 'comment',
        'slack': 'slack',
        'discord': 'discord',
        'whatsapp': 'whatsapp'
    };
    return icons[channelName] || 'bell';
}

/**
 * Get the display name for a channel
 * @param {string} channelName - Name of the channel
 * @returns {string} Display name
 */
export function getChannelDisplayName(channelName) {
    const names = {
        'websocket': 'WebSocket',
        'email': '이메일',
        'kakao': '카카오톡',
        'slack': 'Slack',
        'discord': 'Discord',
        'whatsapp': 'WhatsApp'
    };
    return names[channelName] || channelName;
}

/**
 * Get the appropriate color for a notification type
 * @param {string} type - Notification type
 * @returns {string} Bootstrap color class
 */
export function getTypeColor(type) {
    const colors = {
        'general': 'info',
        'emergency': 'danger',
        'equipment': 'warning',
        'order': 'success',
        'payment': 'primary'
    };
    return colors[type] || 'secondary';
}

/**
 * Get the display name for a notification type
 * @param {string} type - Notification type
 * @returns {string} Display name
 */
export function getTypeDisplayName(type) {
    const names = {
        'general': '일반',
        'emergency': '긴급',
        'equipment': '장비',
        'order': '주문',
        'payment': '결제'
    };
    return names[type] || type;
}

/**
 * Get the appropriate color for a priority level
 * @param {string} priority - Priority level
 * @returns {string} Bootstrap color class
 */
export function getPriorityColor(priority) {
    const colors = {
        'low': 'secondary',
        'normal': 'info',
        'high': 'warning',
        'urgent': 'danger'
    };
    return colors[priority] || 'secondary';
}