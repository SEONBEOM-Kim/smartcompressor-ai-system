class NavigationManager {
    constructor() {
        this.currentSection = 'dashboard';
    }

    navigateToSection(section) {
        document.querySelectorAll('section').forEach(sec => {
            sec.style.display = 'none';
        });

        const targetSection = document.getElementById(`${section}Section`);
        if (targetSection) {
            targetSection.style.display = 'block';
        }

        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`[data-section="${section}"]`)?.classList.add('active');

        this.currentSection = section;
    }

    switchTab(tabName) {
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });

        document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');
        document.getElementById(`${tabName}Tab`)?.classList.add('active');
    }
}

export default NavigationManager;