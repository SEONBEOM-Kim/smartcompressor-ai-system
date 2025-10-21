import { formatTime as commonFormatTime } from '../../../common/utils/formatters.js';

// Export the common formatTime function
export { commonFormatTime as formatTime };

function hideLoadingScreen() {
    const loadingScreen = document.getElementById('loadingScreen');
    const mainApp = document.getElementById('mainApp');
    
    if (loadingScreen && mainApp) {
        loadingScreen.style.opacity = '0';
        setTimeout(() => {
            loadingScreen.style.display = 'none';
            mainApp.style.display = 'block';
            mainApp.style.animation = 'fadeIn 0.5s ease';
        }, 500);
    }
}

export { hideLoadingScreen };