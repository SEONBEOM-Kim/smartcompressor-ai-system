/**
 * Toast Manager for Notification Dashboard
 * Handles toast notifications using Bootstrap
 */

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