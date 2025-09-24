/**
 * 알림 관리 대시보드 JavaScript
 * Slack과 Discord 스타일의 실시간 알림 관리
 */

class NotificationDashboard {
    constructor() {
        this.currentTab = 'overview';
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadOverview();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // 탭 전환
        document.querySelectorAll('[data-tab]').forEach(tab => {
            tab.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchTab(tab.dataset.tab);
            });
        });

        // 빠른 알림 전송 폼
        document.getElementById('quickNotificationForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendQuickNotification();
        });

        // 설정 저장 폼
        document.getElementById('settingsForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.saveSettings();
        });

        // 템플릿 생성 폼
        document.getElementById('templateForm').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createTemplate();
        });
    }

    switchTab(tabName) {
        // 모든 탭 숨기기
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.style.display = 'none';
        });

        // 모든 탭 링크 비활성화
        document.querySelectorAll('[data-tab]').forEach(link => {
            link.classList.remove('active');
        });

        // 선택된 탭 보이기
        document.getElementById(tabName).style.display = 'block';
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        this.currentTab = tabName;

        // 탭별 데이터 로드
        switch (tabName) {
            case 'overview':
                this.loadOverview();
                break;
            case 'channels':
                this.loadChannels();
                break;
            case 'templates':
                this.loadTemplates();
                break;
            case 'history':
                this.loadHistory();
                break;
            case 'settings':
                this.loadSettings();
                break;
        }
    }

    async loadOverview() {
        try {
            // 서비스 상태 로드
            const statusResponse = await fetch('/api/notifications/status');
            const statusData = await statusResponse.json();

            if (statusData.success) {
                this.updateOverviewStats(statusData.status);
            }

            // 채널 상태 로드
            const channelsResponse = await fetch('/api/notifications/channels');
            const channelsData = await channelsResponse.json();

            if (channelsData.success) {
                this.updateChannelStatus(channelsData.channels);
            }

            // 최근 알림 로드
            const historyResponse = await fetch('/api/notifications/history?limit=10');
            const historyData = await historyResponse.json();

            if (historyData.success) {
                this.updateRecentNotifications(historyData.history);
            }

        } catch (error) {
            console.error('개요 데이터 로드 오류:', error);
            this.showToast('데이터 로드 중 오류가 발생했습니다.', 'error');
        }
    }

    updateOverviewStats(status) {
        document.getElementById('totalNotifications').textContent = status.queue_size || 0;
        document.getElementById('successRate').textContent = '95%'; // 실제로는 계산 필요
        document.getElementById('activeChannels').textContent = status.channels.length;
        document.getElementById('queueSize').textContent = status.queue_size || 0;
    }

    updateChannelStatus(channels) {
        const container = document.getElementById('channelStatus');
        container.innerHTML = '';

        Object.entries(channels.channels).forEach(([name, channel]) => {
            const channelDiv = document.createElement('div');
            channelDiv.className = 'col-md-4';
            channelDiv.innerHTML = `
                <div class="channel-status ${channel.status}">
                    <div class="channel-icon">
                        <i class="fas fa-${this.getChannelIcon(name)}"></i>
                    </div>
                    <div class="channel-name">${this.getChannelDisplayName(name)}</div>
                    <div class="channel-status-text">${channel.status}</div>
                    <button class="btn btn-sm btn-outline-light mt-2" onclick="dashboard.testChannel('${name}')">
                        테스트
                    </button>
                </div>
            `;
            container.appendChild(channelDiv);
        });
    }

    updateRecentNotifications(notifications) {
        const tbody = document.getElementById('recentNotifications');
        tbody.innerHTML = '';

        notifications.forEach(notification => {
            const row = document.createElement('tr');
            row.className = `notification-${notification.type}`;
            row.innerHTML = `
                <td>${this.formatDateTime(notification.sent_at)}</td>
                <td><span class="badge badge-${this.getTypeColor(notification.type)}">${this.getTypeDisplayName(notification.type)}</span></td>
                <td>${notification.content}</td>
                <td>${notification.channels.join(', ')}</td>
                <td><span class="badge badge-${this.getPriorityColor(notification.priority)}">${notification.priority}</span></td>
            `;
            tbody.appendChild(row);
        });
    }

    async loadChannels() {
        try {
            const response = await fetch('/api/notifications/channels');
            const data = await response.json();

            if (data.success) {
                this.displayChannels(data.channels);
            }
        } catch (error) {
            console.error('채널 데이터 로드 오류:', error);
            this.showToast('채널 데이터 로드 중 오류가 발생했습니다.', 'error');
        }
    }

    displayChannels(channels) {
        const container = document.getElementById('channelList');
        container.innerHTML = '';

        Object.entries(channels.channels).forEach(([name, channel]) => {
            const channelCard = document.createElement('div');
            channelCard.className = 'col-md-6 mb-3';
            channelCard.innerHTML = `
                <div class="card">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h6 class="card-title mb-0">
                                <i class="fas fa-${this.getChannelIcon(name)} me-2"></i>
                                ${this.getChannelDisplayName(name)}
                            </h6>
                            <span class="badge badge-${channel.status === 'active' ? 'success' : 'danger'}">
                                ${channel.status}
                            </span>
                        </div>
                        <p class="card-text text-muted">
                            마지막 사용: ${this.formatDateTime(channel.last_used)}
                        </p>
                        <div class="d-flex gap-2">
                            <button class="btn btn-sm btn-primary" onclick="dashboard.testChannel('${name}')">
                                <i class="fas fa-play me-1"></i>
                                테스트
                            </button>
                            <button class="btn btn-sm btn-outline-secondary" onclick="dashboard.configureChannel('${name}')">
                                <i class="fas fa-cog me-1"></i>
                                설정
                            </button>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(channelCard);
        });
    }

    async loadTemplates() {
        try {
            const response = await fetch('/api/notifications/email/templates');
            const data = await response.json();

            if (data.success) {
                this.displayTemplates(data.templates);
            }
        } catch (error) {
            console.error('템플릿 데이터 로드 오류:', error);
            this.showToast('템플릿 데이터 로드 중 오류가 발생했습니다.', 'error');
        }
    }

    displayTemplates(templates) {
        const tbody = document.getElementById('templateList');
        tbody.innerHTML = '';

        templates.forEach(template => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${template.template_id}</td>
                <td>${template.name}</td>
                <td><span class="badge badge-info">${template.category}</span></td>
                <td>${template.variables.join(', ')}</td>
                <td><span class="badge badge-${template.is_active ? 'success' : 'secondary'}">${template.is_active ? '활성' : '비활성'}</span></td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="dashboard.editTemplate('${template.template_id}')">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="dashboard.deleteTemplate('${template.template_id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    async loadHistory() {
        try {
            const typeFilter = document.getElementById('historyFilter').value;
            const channelFilter = document.getElementById('channelFilter').value;
            const dateFilter = document.getElementById('dateFilter').value;

            let url = '/api/notifications/history?limit=50';
            if (typeFilter) url += `&type=${typeFilter}`;
            if (channelFilter) url += `&channel=${channelFilter}`;
            if (dateFilter) url += `&date=${dateFilter}`;

            const response = await fetch(url);
            const data = await response.json();

            if (data.success) {
                this.displayHistory(data.history);
            }
        } catch (error) {
            console.error('히스토리 데이터 로드 오류:', error);
            this.showToast('히스토리 데이터 로드 중 오류가 발생했습니다.', 'error');
        }
    }

    displayHistory(history) {
        const tbody = document.getElementById('historyList');
        tbody.innerHTML = '';

        history.forEach(notification => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${this.formatDateTime(notification.sent_at)}</td>
                <td><span class="badge badge-${this.getTypeColor(notification.type)}">${this.getTypeDisplayName(notification.type)}</span></td>
                <td>${notification.content}</td>
                <td>${notification.channels.join(', ')}</td>
                <td><span class="badge badge-${this.getPriorityColor(notification.priority)}">${notification.priority}</span></td>
                <td><span class="badge badge-${notification.status === 'sent' ? 'success' : 'danger'}">${notification.status}</span></td>
            `;
            tbody.appendChild(row);
        });
    }

    async loadSettings() {
        // 설정 데이터 로드 (실제 구현에서는 API에서 가져옴)
        document.getElementById('defaultChannels').value = ['websocket', 'email'];
        document.getElementById('rateLimit').value = 100;
        document.getElementById('emergencyChannels').value = ['websocket', 'slack', 'discord'];
        document.getElementById('autoRetry').checked = true;
    }

    async sendQuickNotification() {
        try {
            const type = document.getElementById('notificationType').value;
            const content = document.getElementById('messageContent').value;
            const channels = Array.from(document.querySelectorAll('input[type="checkbox"]:checked')).map(cb => cb.value);

            if (!content.trim()) {
                this.showToast('메시지를 입력해주세요.', 'warning');
                return;
            }

            const response = await fetch('/api/notifications/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    type: type,
                    content: content,
                    channels: channels,
                    priority: 'normal'
                })
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('알림이 전송되었습니다.', 'success');
                document.getElementById('quickNotificationForm').reset();
                document.getElementById('channelWebSocket').checked = true;
            } else {
                this.showToast('알림 전송에 실패했습니다.', 'error');
            }
        } catch (error) {
            console.error('알림 전송 오류:', error);
            this.showToast('알림 전송 중 오류가 발생했습니다.', 'error');
        }
    }

    async testChannel(channelName) {
        try {
            const response = await fetch(`/api/notifications/test/${channelName}`, {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                this.showToast(`${channelName} 채널 테스트가 성공했습니다.`, 'success');
            } else {
                this.showToast(`${channelName} 채널 테스트가 실패했습니다: ${data.error}`, 'error');
            }
        } catch (error) {
            console.error('채널 테스트 오류:', error);
            this.showToast('채널 테스트 중 오류가 발생했습니다.', 'error');
        }
    }

    async createTemplate() {
        try {
            const templateData = {
                template_id: document.getElementById('templateId').value,
                name: document.getElementById('templateName').value,
                subject: document.getElementById('templateSubject').value,
                html_content: document.getElementById('templateHtml').value,
                text_content: document.getElementById('templateText').value,
                variables: document.getElementById('templateVariables').value.split(',').map(v => v.trim()),
                category: document.getElementById('templateCategory').value
            };

            const response = await fetch('/api/notifications/email/templates', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(templateData)
            });

            const data = await response.json();

            if (data.success) {
                this.showToast('템플릿이 생성되었습니다.', 'success');
                document.getElementById('templateModal').querySelector('.btn-close').click();
                document.getElementById('templateForm').reset();
                this.loadTemplates();
            } else {
                this.showToast('템플릿 생성에 실패했습니다.', 'error');
            }
        } catch (error) {
            console.error('템플릿 생성 오류:', error);
            this.showToast('템플릿 생성 중 오류가 발생했습니다.', 'error');
        }
    }

    async saveSettings() {
        try {
            const settings = {
                default_channels: Array.from(document.getElementById('defaultChannels').selectedOptions).map(o => o.value),
                rate_limit: parseInt(document.getElementById('rateLimit').value),
                emergency_channels: Array.from(document.getElementById('emergencyChannels').selectedOptions).map(o => o.value),
                auto_retry: document.getElementById('autoRetry').checked
            };

            // 실제 구현에서는 API로 설정 저장
            this.showToast('설정이 저장되었습니다.', 'success');
        } catch (error) {
            console.error('설정 저장 오류:', error);
            this.showToast('설정 저장 중 오류가 발생했습니다.', 'error');
        }
    }

    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            if (this.currentTab === 'overview') {
                this.loadOverview();
            }
        }, 30000); // 30초마다 새로고침
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    // 유틸리티 메서드들
    getChannelIcon(channelName) {
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

    getChannelDisplayName(channelName) {
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

    getTypeColor(type) {
        const colors = {
            'general': 'info',
            'emergency': 'danger',
            'equipment': 'warning',
            'order': 'success',
            'payment': 'primary'
        };
        return colors[type] || 'secondary';
    }

    getTypeDisplayName(type) {
        const names = {
            'general': '일반',
            'emergency': '긴급',
            'equipment': '장비',
            'order': '주문',
            'payment': '결제'
        };
        return names[type] || type;
    }

    getPriorityColor(priority) {
        const colors = {
            'low': 'secondary',
            'normal': 'info',
            'high': 'warning',
            'urgent': 'danger'
        };
        return colors[priority] || 'secondary';
    }

    formatDateTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('ko-KR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    showToast(message, type = 'info') {
        // Bootstrap 토스트 생성
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        
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
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // 토스트가 사라진 후 DOM에서 제거
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    }
}

// 전역 함수들
function loadHistory() {
    dashboard.loadHistory();
}

function createTemplate() {
    dashboard.createTemplate();
}

// 페이지 로드 시 대시보드 초기화
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new NotificationDashboard();
});
