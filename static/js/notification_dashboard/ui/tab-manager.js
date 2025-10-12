/**
 * Tab Manager for Notification Dashboard
 * Handles tab switching logic and state management
 */

class TabManager {
    constructor(onTabSwitchCallback) {
        this.currentTab = 'overview';
        this.onTabSwitchCallback = onTabSwitchCallback;
        this.init();
    }

    init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Add event listeners for all tab elements
        document.querySelectorAll('[data-tab]').forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchTab(tab.dataset.tab);
            });
        });
    }

    switchTab(tabName) {
        // Hide all tab content areas
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.style.display = 'none';
        });

        // Remove active class from all tab links
        document.querySelectorAll('[data-tab]').forEach(link => {
            link.classList.remove('active');
        });

        // Show selected tab content
        const selectedTabContent = document.getElementById(tabName);
        if (selectedTabContent) {
            selectedTabContent.style.display = 'block';
        }

        // Add active class to selected tab link
        const selectedTabLink = document.querySelector(`[data-tab="${tabName}"]`);
        if (selectedTabLink) {
            selectedTabLink.classList.add('active');
        }

        this.currentTab = tabName;

        // Call the callback function to handle tab-specific data loading
        if (this.onTabSwitchCallback) {
            this.onTabSwitchCallback(tabName);
        }
    }

    getCurrentTab() {
        return this.currentTab;
    }
}

// Export the class for use in other modules
export default TabManager;