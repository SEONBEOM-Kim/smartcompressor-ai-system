function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;

    if (diff < 60000) {
        return '방금 전';
    } else if (diff < 3600000) {
        return `${Math.floor(diff / 60000)}분 전`;
    } else if (diff < 86400000) {
        return `${Math.floor(diff / 3600000)}시간 전`;
    } else {
        return date.toLocaleDateString('ko-KR');
    }
}

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

export { formatTime, hideLoadingScreen };