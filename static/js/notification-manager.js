// 실시간 알림 관리자
class NotificationManager {
    constructor() {
        this.notifications = [];
        this.isConnected = false;
        this.retryCount = 0;
        this.maxRetries = 5;
        this.retryDelay = 1000;
        
        this.init();
    }
    
    init() {
        this.setupEventSource();
        this.setupNotificationPermission();
        this.setupUI();
    }
    
    setupEventSource() {
        // Server-Sent Events로 실시간 알림 수신
        this.eventSource = new EventSource('/api/notifications/stream');
        
        this.eventSource.onopen = () => {
            console.log('알림 스트림 연결됨');
            this.isConnected = true;
            this.retryCount = 0;
            this.updateConnectionStatus('connected');
        };
        
        this.eventSource.onmessage = (event) => {
            try {
                const notification = JSON.parse(event.data);
                this.handleNotification(notification);
            } catch (error) {
                console.error('알림 파싱 오류:', error);
            }
        };
        
        this.eventSource.onerror = () => {
            console.log('알림 스트림 연결 오류');
            this.isConnected = false;
            this.updateConnectionStatus('disconnected');
            this.retryConnection();
        };
    }
    
    retryConnection() {
        if (this.retryCount < this.maxRetries) {
            this.retryCount++;
            console.log(`알림 스트림 재연결 시도 ${this.retryCount}/${this.maxRetries}`);
            
            setTimeout(() => {
                this.setupEventSource();
            }, this.retryDelay * this.retryCount);
        } else {
            console.error('알림 스트림 재연결 실패');
            this.updateConnectionStatus('failed');
        }
    }
    
    setupNotificationPermission() {
        if ('Notification' in window) {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    console.log('브라우저 알림 권한 허용됨');
                }
            });
        }
    }
    
    setupUI() {
        // 알림 벨 아이콘 추가
        this.createNotificationIcon();
        this.createNotificationPanel();
    }
    
    createNotificationIcon() {
        const navbar = document.querySelector('.navbar-nav');
        if (navbar) {
            const notificationItem = document.createElement('li');
            notificationItem.className = 'nav-item dropdown';
            notificationItem.innerHTML = `
                <a class="nav-link position-relative" href="#" role="button" data-bs-toggle="dropdown">
                    <i class="fas fa-bell"></i>
                    <span id="notification-badge" class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" style="display: none;">
                        0
                    </span>
                </a>
                <ul class="dropdown-menu dropdown-menu-end notification-dropdown" style="width: 350px;">
                    <li class="dropdown-header d-flex justify-content-between align-items-center">
                        <span>알림</span>
                        <button class="btn btn-sm btn-outline-secondary" onclick="notificationManager.markAllAsRead()">
                            모두 읽음
                        </button>
                    </li>
                    <li><hr class="dropdown-divider"></li>
                    <div id="notification-list" class="notification-list">
                        <div class="text-center text-muted p-3">
                            <i class="fas fa-bell-slash fa-2x mb-2"></i>
                            <p>새로운 알림이 없습니다</p>
                        </div>
                    </div>
                    <li><hr class="dropdown-divider"></li>
                    <li>
                        <a class="dropdown-item text-center" href="#" onclick="notificationManager.showAllNotifications()">
                            모든 알림 보기
                        </a>
                    </li>
                </ul>
            `;
            navbar.appendChild(notificationItem);
        }
    }
    
    createNotificationPanel() {
        // 전체 알림 패널 생성
        const notificationPanel = document.createElement('div');
        notificationPanel.id = 'notification-panel';
        notificationPanel.className = 'modal fade';
        notificationPanel.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-bell me-2"></i>알림 관리
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row mb-3">
                            <div class="col-md-6">
                                <div class="btn-group" role="group">
                                    <input type="radio" class="btn-check" name="filter" id="filter-all" checked>
                                    <label class="btn btn-outline-primary" for="filter-all">전체</label>
                                    
                                    <input type="radio" class="btn-check" name="filter" id="filter-unread">
                                    <label class="btn btn-outline-primary" for="filter-unread">읽지 않음</label>
                                    
                                    <input type="radio" class="btn-check" name="filter" id="filter-critical">
                                    <label class="btn btn-outline-danger" for="filter-critical">긴급</label>
                                </div>
                            </div>
                            <div class="col-md-6 text-end">
                                <button class="btn btn-outline-secondary btn-sm" onclick="notificationManager.refreshNotifications()">
                                    <i class="fas fa-sync-alt me-1"></i>새로고침
                                </button>
                            </div>
                        </div>
                        <div id="notification-panel-list" class="notification-panel-list">
                            <!-- 알림 목록이 여기에 표시됩니다 -->
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(notificationPanel);
    }
    
    handleNotification(notification) {
        console.log('새 알림 수신:', notification);
        
        // 알림 목록에 추가
        this.notifications.unshift(notification);
        
        // 최대 100개까지만 유지
        if (this.notifications.length > 100) {
            this.notifications = this.notifications.slice(0, 100);
        }
        
        // UI 업데이트
        this.updateNotificationBadge();
        this.updateNotificationList();
        
        // 브라우저 알림 표시
        this.showBrowserNotification(notification);
        
        // 소리 재생 (긴급 알림)
        if (notification.severity === 'critical') {
            this.playAlertSound();
        }
    }
    
    showBrowserNotification(notification) {
        if (Notification.permission === 'granted') {
            const browserNotification = new Notification(
                `Signalcraft 알림 - ${notification.alert_type}`,
                {
                    body: notification.message,
                    icon: '/static/favicon.ico',
                    badge: '/static/favicon.ico',
                    tag: notification.alert_id,
                    requireInteraction: notification.severity === 'critical'
                }
            );
            
            browserNotification.onclick = () => {
                window.focus();
                browserNotification.close();
            };
            
            // 5초 후 자동 닫기 (긴급 알림 제외)
            if (notification.severity !== 'critical') {
                setTimeout(() => {
                    browserNotification.close();
                }, 5000);
            }
        }
    }
    
    playAlertSound() {
        // 알림 소리 재생
        const audio = new Audio('/static/sounds/alert.mp3');
        audio.volume = 0.5;
        audio.play().catch(e => console.log('알림 소리 재생 실패:', e));
    }
    
    updateNotificationBadge() {
        const unreadCount = this.notifications.filter(n => !n.read).length;
        const badge = document.getElementById('notification-badge');
        
        if (unreadCount > 0) {
            badge.textContent = unreadCount;
            badge.style.display = 'block';
        } else {
            badge.style.display = 'none';
        }
    }
    
    updateNotificationList() {
        const list = document.getElementById('notification-list');
        if (!list) return;
        
        const recentNotifications = this.notifications.slice(0, 5);
        
        if (recentNotifications.length === 0) {
            list.innerHTML = `
                <div class="text-center text-muted p-3">
                    <i class="fas fa-bell-slash fa-2x mb-2"></i>
                    <p>새로운 알림이 없습니다</p>
                </div>
            `;
            return;
        }
        
        list.innerHTML = recentNotifications.map(notification => `
            <li class="notification-item ${notification.read ? '' : 'unread'}" data-alert-id="${notification.alert_id}">
                <div class="d-flex align-items-start p-2">
                    <div class="notification-icon me-3">
                        <i class="fas fa-${this.getNotificationIcon(notification.alert_type)} text-${this.getSeverityColor(notification.severity)}"></i>
                    </div>
                    <div class="notification-content flex-grow-1">
                        <div class="notification-title">${notification.alert_type}</div>
                        <div class="notification-message">${notification.message}</div>
                        <div class="notification-time">${this.formatTime(notification.timestamp)}</div>
                    </div>
                    <div class="notification-actions">
                        <button class="btn btn-sm btn-outline-secondary" onclick="notificationManager.markAsRead('${notification.alert_id}')">
                            <i class="fas fa-check"></i>
                        </button>
                    </div>
                </div>
            </li>
        `).join('');
    }
    
    getNotificationIcon(alertType) {
        const icons = {
            'compressor_anomaly': 'exclamation-triangle',
            'temperature_anomaly': 'thermometer-half',
            'vibration_anomaly': 'wave-square',
            'connection_lost': 'wifi',
            'device_offline': 'power-off',
            'maintenance_required': 'wrench'
        };
        return icons[alertType] || 'bell';
    }
    
    getSeverityColor(severity) {
        const colors = {
            'low': 'info',
            'medium': 'warning',
            'high': 'danger',
            'critical': 'danger'
        };
        return colors[severity] || 'secondary';
    }
    
    formatTime(timestamp) {
        const now = Date.now() / 1000;
        const diff = now - timestamp;
        
        if (diff < 60) return '방금 전';
        if (diff < 3600) return `${Math.floor(diff / 60)}분 전`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}시간 전`;
        return new Date(timestamp * 1000).toLocaleDateString();
    }
    
    markAsRead(alertId) {
        const notification = this.notifications.find(n => n.alert_id === alertId);
        if (notification) {
            notification.read = true;
            this.updateNotificationBadge();
            this.updateNotificationList();
        }
    }
    
    markAllAsRead() {
        this.notifications.forEach(n => n.read = true);
        this.updateNotificationBadge();
        this.updateNotificationList();
    }
    
    showAllNotifications() {
        const modal = new bootstrap.Modal(document.getElementById('notification-panel'));
        modal.show();
        this.updateNotificationPanel();
    }
    
    updateNotificationPanel() {
        const panelList = document.getElementById('notification-panel-list');
        if (!panelList) return;
        
        panelList.innerHTML = this.notifications.map(notification => `
            <div class="notification-panel-item ${notification.read ? '' : 'unread'} mb-3 p-3 border rounded">
                <div class="d-flex align-items-start">
                    <div class="notification-icon me-3">
                        <i class="fas fa-${this.getNotificationIcon(notification.alert_type)} text-${this.getSeverityColor(notification.severity)} fa-2x"></i>
                    </div>
                    <div class="notification-content flex-grow-1">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <h6 class="notification-title mb-0">${notification.alert_type}</h6>
                            <span class="badge bg-${this.getSeverityColor(notification.severity)}">${notification.severity}</span>
                        </div>
                        <p class="notification-message mb-2">${notification.message}</p>
                        <div class="notification-meta">
                            <small class="text-muted">
                                <i class="fas fa-clock me-1"></i>
                                ${this.formatTime(notification.timestamp)}
                                <span class="ms-3">
                                    <i class="fas fa-microchip me-1"></i>
                                    ${notification.device_id}
                                </span>
                            </small>
                        </div>
                    </div>
                    <div class="notification-actions">
                        <button class="btn btn-sm btn-outline-primary" onclick="notificationManager.viewDetails('${notification.alert_id}')">
                            <i class="fas fa-eye"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="notificationManager.markAsRead('${notification.alert_id}')">
                            <i class="fas fa-check"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    viewDetails(alertId) {
        const notification = this.notifications.find(n => n.alert_id === alertId);
        if (notification) {
            alert(`알림 상세 정보:\n\n유형: ${notification.alert_type}\n심각도: ${notification.severity}\n메시지: ${notification.message}\n시간: ${new Date(notification.timestamp * 1000).toLocaleString()}\n디바이스: ${notification.device_id}`);
        }
    }
    
    refreshNotifications() {
        // 서버에서 최신 알림 목록 가져오기
        fetch('/api/notifications')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.notifications = data.notifications;
                    this.updateNotificationList();
                    this.updateNotificationPanel();
                }
            })
            .catch(error => {
                console.error('알림 새로고침 실패:', error);
            });
    }
    
    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            statusElement.textContent = status;
            statusElement.className = `badge bg-${status === 'connected' ? 'success' : 'danger'}`;
        }
    }
}

// 전역 인스턴스 생성
const notificationManager = new NotificationManager();
