class PWAManager {
    constructor() {
        this.deferredPrompt = null;
    }

    async init() {
        await this.registerServiceWorker();
        await this.requestNotificationPermission();
        this.setupInstallPrompt();
        this.registerBackgroundSync();
    }

    async registerServiceWorker() {
        if ('serviceWorker' in navigator) {
            try {
                const registration = await navigator.serviceWorker.ready;
                console.log('✅ Service Worker 준비 완료');
                
                // 백그라운드 동기화 등록
                if ('sync' in window.ServiceWorkerRegistration.prototype) {
                    await registration.sync.register('offline-data-sync');
                }
            } catch (error) {
                console.error('❌ Service Worker 오류:', error);
            }
        }
    }

    async requestNotificationPermission() {
        if ('Notification' in window) {
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                console.log('✅ 푸시 알림 권한 허용됨');
                return true;
            } else {
                console.log('❌ 푸시 알림 권한 거부됨');
                return false;
            }
        }
        return false;
    }

    setupInstallPrompt() {
        // PWA 설치 프롬프트
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallPrompt(this.deferredPrompt);
        });
    }

    showInstallPrompt(deferredPrompt) {
        // In a real implementation, this would trigger UI to show install prompt
        // For now, we'll just log that we can prompt the user
        console.log('앱을 홈 화면에 설치하시겠습니까?');
    }
    
    async registerBackgroundSync() {
        // This method registers background sync which is already handled 
        // in registerServiceWorker method above
    }
}

// PWA 설치 이벤트
window.addEventListener('appinstalled', () => {
    console.log('✅ PWA가 설치되었습니다');
});

export default PWAManager;