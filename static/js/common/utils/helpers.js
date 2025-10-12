/**
 * Common helpers for all modules
 * Consolidates duplicated helper functions from various modules
 */

/**
 * Show an alert message at the top-right of the screen
 * @param {string} message - Message to display
 * @param {string} type - Type of alert (success, info, warning, danger)
 */
export function showAlert(message, type = 'info') {
    // 기존 알림이 있다면 제거
    const existingAlerts = document.querySelectorAll('.alert.position-fixed');
    existingAlerts.forEach(alert => alert.remove());

    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(alertDiv);

    // 5초 후 자동 제거
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

/**
 * Show a toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type of toast (info, success, warning, error)
 */
export function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    // Add toast to container
    toastContainer.appendChild(toast);
    
    // Initialize and show the toast
    if (window.bootstrap && bootstrap.Toast) {
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast from DOM when it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    } else {
        // Fallback if Bootstrap JS is not loaded
        toast.classList.add('show');
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }
}

/**
 * Create the toast container element
 * @returns {HTMLElement} Toast container element
 */
function createToastContainer() {
    let container = document.getElementById('toast-container');
    
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    
    return container;
}

/**
 * Start auto-refresh with interval
 * @param {Function} callback - Function to call on each interval
 * @param {number} interval - Interval in milliseconds (default 30s)
 * @returns {number} Interval ID
 */
export function startAutoRefreshHelper(callback, interval = 30000) {
    return setInterval(callback, interval);
}

/**
 * Stop auto-refresh
 * @param {number} intervalId - Interval ID returned by startAutoRefreshHelper
 */
export function stopAutoRefreshHelper(intervalId) {
    if (intervalId) {
        clearInterval(intervalId);
    }
}

/**
 * Open a Bootstrap modal by ID
 * @param {string} modalId - ID of the modal to open
 * @returns {bootstrap.Modal|undefined} Modal instance
 */
export function openModal(modalId) {
    const modalElement = document.getElementById(modalId);
    if (modalElement && window.bootstrap && window.bootstrap.Modal) {
        const modal = new window.bootstrap.Modal(modalElement);
        modal.show();
        return modal;
    }
}

/**
 * Close a Bootstrap modal by ID
 * @param {string} modalId - ID of the modal to close
 */
export function closeModal(modalId) {
    const modalElement = document.getElementById(modalId);
    if (modalElement && window.bootstrap && window.bootstrap.Modal) {
        const modal = window.bootstrap.Modal.getInstance(modalElement);
        if (modal) {
            modal.hide();
        }
    }
}

/**
 * Handle online/offline status changes
 * @param {boolean} isOnline - Whether the connection is online
 * @param {Function} callback - Optional callback function
 */
export function handleOnlineStatus(isOnline, callback) {
    const statusIndicator = document.getElementById('connectionStatus');
    if (statusIndicator) {
        const icon = statusIndicator.querySelector('i');
        if (isOnline) {
            icon.className = 'fas fa-wifi';
            icon.style.color = 'var(--status-normal)';
        } else {
            icon.className = 'fas fa-wifi-slash';
            icon.style.color = 'var(--status-error)';
            showOfflineModal();
        }
    }
    
    if (callback && typeof callback === 'function') {
        callback(isOnline);
    }
}

/**
 * Show offline modal
 */
export function showOfflineModal() {
    const modal = new bootstrap.Modal(document.getElementById('offlineModal'));
    modal.show();
}