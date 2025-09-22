// Admin Dashboard JavaScript - AWS Management Console & GitHub 벤치마킹

class AdminDashboard {
    constructor() {
        this.currentSection = 'dashboard';
        this.charts = {};
        this.data = {
            stores: [],
            users: [],
            tickets: [],
            logs: [],
            securityEvents: [],
            backups: [],
            performanceAlerts: []
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboardData();
        this.initializeCharts();
        this.startRealTimeUpdates();
    }

    setupEventListeners() {
        // Sidebar navigation
        document.querySelectorAll('.menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const section = item.getAttribute('data-section');
                this.showSection(section);
            });
        });

        // Sidebar toggle for mobile
        const sidebarToggle = document.querySelector('.sidebar-toggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => {
                document.querySelector('.sidebar').classList.toggle('show');
            });
        }

        // Search functionality
        const searchInputs = document.querySelectorAll('input[type="text"]');
        searchInputs.forEach(input => {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch(input.id);
                }
            });
        });

        // Filter changes
        const filters = document.querySelectorAll('select');
        filters.forEach(filter => {
            filter.addEventListener('change', () => {
                this.applyFilters();
            });
        });
    }

    showSection(sectionName) {
        // Hide all sections
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.remove('active');
        });

        // Remove active class from menu items
        document.querySelectorAll('.menu-item').forEach(item => {
            item.classList.remove('active');
        });

        // Show selected section
        const targetSection = document.getElementById(sectionName + 'Section');
        if (targetSection) {
            targetSection.classList.add('active');
        }

        // Add active class to menu item
        const menuItem = document.querySelector(`[data-section="${sectionName}"]`);
        if (menuItem) {
            menuItem.classList.add('active');
        }

        this.currentSection = sectionName;

        // Load section-specific data
        this.loadSectionData(sectionName);
    }

    async loadDashboardData() {
        try {
            // Load overview statistics
            const response = await fetch('/api/admin/overview');
            const data = await response.json();
            
            if (data.success) {
                this.updateOverviewStats(data.data);
            }
        } catch (error) {
            console.error('Failed to load dashboard data:', error);
            this.showError('대시보드 데이터를 불러오는데 실패했습니다.');
        }
    }

    updateOverviewStats(stats) {
        document.getElementById('totalStores').textContent = stats.totalStores || 0;
        document.getElementById('totalUsers').textContent = stats.totalUsers || 0;
        document.getElementById('openTickets').textContent = stats.openTickets || 0;
        document.getElementById('activeAlerts').textContent = stats.activeAlerts || 0;
    }

    async loadSectionData(sectionName) {
        switch (sectionName) {
            case 'stores':
                await this.loadStoresData();
                break;
            case 'users':
                await this.loadUsersData();
                break;
            case 'monitoring':
                await this.loadMonitoringData();
                break;
            case 'logs':
                await this.loadLogsData();
                break;
            case 'tickets':
                await this.loadTicketsData();
                break;
            case 'security':
                await this.loadSecurityData();
                break;
            case 'backup':
                await this.loadBackupData();
                break;
            case 'performance':
                await this.loadPerformanceData();
                break;
        }
    }

    async loadStoresData() {
        try {
            const response = await fetch('/api/admin/stores');
            const data = await response.json();
            
            if (data.success) {
                this.data.stores = data.data;
                this.renderStoresTable();
            }
        } catch (error) {
            console.error('Failed to load stores data:', error);
        }
    }

    renderStoresTable() {
        const tbody = document.querySelector('#storesTable tbody');
        tbody.innerHTML = '';

        this.data.stores.forEach(store => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${store.name}</td>
                <td>${store.owner_name}</td>
                <td><span class="badge bg-${this.getStatusColor(store.status)}">${this.getStatusText(store.status)}</span></td>
                <td>${store.type}</td>
                <td>${this.formatDate(store.created_at)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="adminDashboard.editStore('${store.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="adminDashboard.deleteStore('${store.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    async loadUsersData() {
        try {
            const response = await fetch('/api/admin/users');
            const data = await response.json();
            
            if (data.success) {
                this.data.users = data.data;
                this.renderUsersTable();
            }
        } catch (error) {
            console.error('Failed to load users data:', error);
        }
    }

    renderUsersTable() {
        const tbody = document.querySelector('#usersTable tbody');
        tbody.innerHTML = '';

        this.data.users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.username}</td>
                <td>${user.email}</td>
                <td><span class="badge bg-info">${this.getRoleText(user.role)}</span></td>
                <td><span class="badge bg-${user.is_active ? 'success' : 'danger'}">${user.is_active ? '활성' : '비활성'}</span></td>
                <td>${this.formatDate(user.last_login)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="adminDashboard.editUser('${user.id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="adminDashboard.deleteUser('${user.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    async loadMonitoringData() {
        try {
            const response = await fetch('/api/admin/monitoring');
            const data = await response.json();
            
            if (data.success) {
                this.renderServiceStatusCards(data.data.services);
                this.updateMonitoringCharts(data.data.metrics);
            }
        } catch (error) {
            console.error('Failed to load monitoring data:', error);
        }
    }

    renderServiceStatusCards(services) {
        const container = document.getElementById('serviceStatusCards');
        container.innerHTML = '';

        services.forEach(service => {
            const card = document.createElement('div');
            card.className = 'col-md-3';
            card.innerHTML = `
                <div class="service-status-card">
                    <h6>${service.name}</h6>
                    <div class="status-indicator ${service.status}"></div>
                    <p class="mb-0">${this.getStatusText(service.status)}</p>
                    <small class="text-muted">${service.uptime}%</small>
                </div>
            `;
            container.appendChild(card);
        });
    }

    async loadLogsData() {
        try {
            const response = await fetch('/api/admin/logs');
            const data = await response.json();
            
            if (data.success) {
                this.data.logs = data.data;
                this.renderLogsTable();
            }
        } catch (error) {
            console.error('Failed to load logs data:', error);
        }
    }

    renderLogsTable() {
        const tbody = document.querySelector('#logsTable tbody');
        tbody.innerHTML = '';

        this.data.logs.forEach(log => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${this.formatDateTime(log.timestamp)}</td>
                <td><span class="badge bg-${this.getLogLevelColor(log.level)}">${log.level}</span></td>
                <td>${log.source}</td>
                <td>${log.service}</td>
                <td>${log.message}</td>
            `;
            tbody.appendChild(row);
        });
    }

    async loadTicketsData() {
        try {
            const response = await fetch('/api/admin/tickets');
            const data = await response.json();
            
            if (data.success) {
                this.data.tickets = data.data;
                this.updateTicketStats(data.stats);
                this.renderTicketsTable();
            }
        } catch (error) {
            console.error('Failed to load tickets data:', error);
        }
    }

    updateTicketStats(stats) {
        document.getElementById('totalTickets').textContent = stats.total || 0;
        document.getElementById('openTicketsCount').textContent = stats.open || 0;
        document.getElementById('resolvedTickets').textContent = stats.resolved || 0;
        document.getElementById('urgentTickets').textContent = stats.urgent || 0;
    }

    renderTicketsTable() {
        const tbody = document.querySelector('#ticketsTable tbody');
        tbody.innerHTML = '';

        this.data.tickets.forEach(ticket => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>#${ticket.id}</td>
                <td>${ticket.title}</td>
                <td>${ticket.customer_name}</td>
                <td><span class="badge bg-${this.getPriorityColor(ticket.priority)}">${this.getPriorityText(ticket.priority)}</span></td>
                <td><span class="badge bg-${this.getStatusColor(ticket.status)}">${this.getStatusText(ticket.status)}</span></td>
                <td>${ticket.assignee || '미할당'}</td>
                <td>${this.formatDate(ticket.created_at)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="adminDashboard.viewTicket('${ticket.id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-success" onclick="adminDashboard.assignTicket('${ticket.id}')">
                        <i class="fas fa-user-plus"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    async loadSecurityData() {
        try {
            const response = await fetch('/api/admin/security');
            const data = await response.json();
            
            if (data.success) {
                this.updateSecurityStats(data.stats);
                this.data.securityEvents = data.events;
                this.renderSecurityEventsTable();
            }
        } catch (error) {
            console.error('Failed to load security data:', error);
        }
    }

    updateSecurityStats(stats) {
        document.getElementById('securityEvents').textContent = stats.events || 0;
        document.getElementById('securityAlerts').textContent = stats.alerts || 0;
        document.getElementById('blockedIPs').textContent = stats.blocked_ips || 0;
        document.getElementById('activeUsers').textContent = stats.active_users || 0;
    }

    renderSecurityEventsTable() {
        const tbody = document.querySelector('#securityEventsTable tbody');
        tbody.innerHTML = '';

        this.data.securityEvents.forEach(event => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${this.formatDateTime(event.timestamp)}</td>
                <td>${event.event_type}</td>
                <td>${event.user || 'N/A'}</td>
                <td>${event.ip_address}</td>
                <td>${event.description}</td>
                <td><span class="badge bg-${this.getRiskColor(event.risk_level)}">${this.getRiskText(event.risk_level)}</span></td>
            `;
            tbody.appendChild(row);
        });
    }

    async loadBackupData() {
        try {
            const response = await fetch('/api/admin/backups');
            const data = await response.json();
            
            if (data.success) {
                this.updateBackupStats(data.stats);
                this.data.backups = data.data;
                this.renderBackupsTable();
            }
        } catch (error) {
            console.error('Failed to load backup data:', error);
        }
    }

    updateBackupStats(stats) {
        document.getElementById('totalBackups').textContent = stats.total || 0;
        document.getElementById('completedBackups').textContent = stats.completed || 0;
        document.getElementById('backupSize').textContent = this.formatBytes(stats.total_size || 0);
        document.getElementById('lastBackup').textContent = stats.last_backup ? this.formatDate(stats.last_backup) : 'N/A';
    }

    renderBackupsTable() {
        const tbody = document.querySelector('#backupsTable tbody');
        tbody.innerHTML = '';

        this.data.backups.forEach(backup => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${backup.name}</td>
                <td><span class="badge bg-info">${backup.type}</span></td>
                <td><span class="badge bg-${this.getStatusColor(backup.status)}">${this.getStatusText(backup.status)}</span></td>
                <td>${this.formatBytes(backup.size)}</td>
                <td>${this.formatDate(backup.created_at)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="adminDashboard.downloadBackup('${backup.id}')">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="adminDashboard.deleteBackup('${backup.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    async loadPerformanceData() {
        try {
            const response = await fetch('/api/admin/performance');
            const data = await response.json();
            
            if (data.success) {
                this.updatePerformanceCharts(data.metrics);
                this.data.performanceAlerts = data.alerts;
                this.renderPerformanceAlertsTable();
            }
        } catch (error) {
            console.error('Failed to load performance data:', error);
        }
    }

    renderPerformanceAlertsTable() {
        const tbody = document.querySelector('#performanceAlertsTable tbody');
        tbody.innerHTML = '';

        this.data.performanceAlerts.forEach(alert => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${alert.service}</td>
                <td>${alert.metric}</td>
                <td>${alert.current_value}</td>
                <td>${alert.threshold}</td>
                <td><span class="badge bg-${this.getAlertLevelColor(alert.level)}">${this.getAlertLevelText(alert.level)}</span></td>
                <td>${this.formatDateTime(alert.timestamp)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="adminDashboard.acknowledgeAlert('${alert.id}')">
                        <i class="fas fa-check"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    initializeCharts() {
        this.initializeServiceStatusChart();
        this.initializeResourceUsageChart();
        this.initializeCPUMemoryCharts();
        this.initializePerformanceCharts();
    }

    initializeServiceStatusChart() {
        const ctx = document.getElementById('serviceStatusChart');
        if (!ctx) return;

        this.charts.serviceStatus = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['정상', '경고', '오류', '알 수 없음'],
                datasets: [{
                    data: [85, 10, 3, 2],
                    backgroundColor: ['#28a745', '#ffc107', '#dc3545', '#6c757d'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    initializeResourceUsageChart() {
        const ctx = document.getElementById('resourceUsageChart');
        if (!ctx) return;

        this.charts.resourceUsage = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['CPU', '메모리', '디스크', '네트워크'],
                datasets: [{
                    label: '사용률 (%)',
                    data: [65, 78, 45, 32],
                    backgroundColor: ['#007bff', '#28a745', '#ffc107', '#dc3545'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }

    initializeCPUMemoryCharts() {
        // CPU Chart
        const cpuCtx = document.getElementById('cpuChart');
        if (cpuCtx) {
            this.charts.cpu = new Chart(cpuCtx, {
                type: 'line',
                data: {
                    labels: this.generateTimeLabels(24),
                    datasets: [{
                        label: 'CPU 사용률 (%)',
                        data: this.generateRandomData(24, 0, 100),
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0, 123, 255, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }

        // Memory Chart
        const memoryCtx = document.getElementById('memoryChart');
        if (memoryCtx) {
            this.charts.memory = new Chart(memoryCtx, {
                type: 'line',
                data: {
                    labels: this.generateTimeLabels(24),
                    datasets: [{
                        label: '메모리 사용률 (%)',
                        data: this.generateRandomData(24, 0, 100),
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40, 167, 69, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }
    }

    initializePerformanceCharts() {
        // Response Time Chart
        const responseCtx = document.getElementById('responseTimeChart');
        if (responseCtx) {
            this.charts.responseTime = new Chart(responseCtx, {
                type: 'line',
                data: {
                    labels: this.generateTimeLabels(24),
                    datasets: [{
                        label: '응답 시간 (ms)',
                        data: this.generateRandomData(24, 50, 500),
                        borderColor: '#ffc107',
                        backgroundColor: 'rgba(255, 193, 7, 0.1)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }

        // Request Rate Chart
        const requestCtx = document.getElementById('requestRateChart');
        if (requestCtx) {
            this.charts.requestRate = new Chart(requestCtx, {
                type: 'bar',
                data: {
                    labels: this.generateTimeLabels(24),
                    datasets: [{
                        label: '요청률 (req/min)',
                        data: this.generateRandomData(24, 0, 1000),
                        backgroundColor: '#17a2b8',
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        }
    }

    updateMonitoringCharts(metrics) {
        if (this.charts.cpu && metrics.cpu) {
            this.charts.cpu.data.datasets[0].data = metrics.cpu;
            this.charts.cpu.update();
        }

        if (this.charts.memory && metrics.memory) {
            this.charts.memory.data.datasets[0].data = metrics.memory;
            this.charts.memory.update();
        }
    }

    updatePerformanceCharts(metrics) {
        if (this.charts.responseTime && metrics.responseTime) {
            this.charts.responseTime.data.datasets[0].data = metrics.responseTime;
            this.charts.responseTime.update();
        }

        if (this.charts.requestRate && metrics.requestRate) {
            this.charts.requestRate.data.datasets[0].data = metrics.requestRate;
            this.charts.requestRate.update();
        }
    }

    startRealTimeUpdates() {
        // Update data every 30 seconds
        setInterval(() => {
            this.loadDashboardData();
            if (this.currentSection === 'monitoring') {
                this.loadMonitoringData();
            }
        }, 30000);
    }

    // Utility Methods
    getStatusColor(status) {
        const colors = {
            'active': 'success',
            'inactive': 'secondary',
            'suspended': 'danger',
            'healthy': 'success',
            'warning': 'warning',
            'error': 'danger',
            'completed': 'success',
            'pending': 'warning',
            'failed': 'danger'
        };
        return colors[status] || 'secondary';
    }

    getStatusText(status) {
        const texts = {
            'active': '활성',
            'inactive': '비활성',
            'suspended': '정지',
            'healthy': '정상',
            'warning': '경고',
            'error': '오류',
            'completed': '완료',
            'pending': '대기',
            'failed': '실패'
        };
        return texts[status] || status;
    }

    getRoleText(role) {
        const roles = {
            'admin': '관리자',
            'store_owner': '매장 주인',
            'store_manager': '매장 관리자',
            'technician': '기술자',
            'customer_support': '고객 지원',
            'viewer': '조회자'
        };
        return roles[role] || role;
    }

    getLogLevelColor(level) {
        const colors = {
            'DEBUG': 'secondary',
            'INFO': 'info',
            'WARNING': 'warning',
            'ERROR': 'danger',
            'CRITICAL': 'danger'
        };
        return colors[level] || 'secondary';
    }

    getPriorityColor(priority) {
        const colors = {
            'low': 'info',
            'medium': 'warning',
            'high': 'danger',
            'urgent': 'danger'
        };
        return colors[priority] || 'secondary';
    }

    getPriorityText(priority) {
        const texts = {
            'low': '낮음',
            'medium': '보통',
            'high': '높음',
            'urgent': '긴급'
        };
        return texts[priority] || priority;
    }

    getRiskColor(risk) {
        const colors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
            'critical': 'danger'
        };
        return colors[risk] || 'secondary';
    }

    getRiskText(risk) {
        const texts = {
            'low': '낮음',
            'medium': '보통',
            'high': '높음',
            'critical': '위험'
        };
        return texts[risk] || risk;
    }

    getAlertLevelColor(level) {
        const colors = {
            'info': 'info',
            'warning': 'warning',
            'error': 'danger',
            'critical': 'danger'
        };
        return colors[level] || 'secondary';
    }

    getAlertLevelText(level) {
        const texts = {
            'info': '정보',
            'warning': '경고',
            'error': '오류',
            'critical': '위험'
        };
        return texts[level] || level;
    }

    formatDate(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('ko-KR');
    }

    formatDateTime(dateString) {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleString('ko-KR');
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    generateTimeLabels(hours) {
        const labels = [];
        const now = new Date();
        for (let i = hours - 1; i >= 0; i--) {
            const time = new Date(now.getTime() - i * 60 * 60 * 1000);
            labels.push(time.getHours() + ':00');
        }
        return labels;
    }

    generateRandomData(count, min, max) {
        const data = [];
        for (let i = 0; i < count; i++) {
            data.push(Math.floor(Math.random() * (max - min + 1)) + min);
        }
        return data;
    }

    showError(message) {
        // Simple error notification
        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show position-fixed';
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alert);

        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 5000);
    }

    showSuccess(message) {
        // Simple success notification
        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show position-fixed';
        alert.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alert);

        // Auto remove after 3 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 3000);
    }

    // Modal Functions
    showStoreModal(storeId = null) {
        const modal = new bootstrap.Modal(document.getElementById('storeModal'));
        if (storeId) {
            // Load store data for editing
            this.loadStoreData(storeId);
        } else {
            // Clear form for new store
            document.getElementById('storeForm').reset();
        }
        modal.show();
    }

    showUserModal(userId = null) {
        const modal = new bootstrap.Modal(document.getElementById('userModal'));
        if (userId) {
            // Load user data for editing
            this.loadUserData(userId);
        } else {
            // Clear form for new user
            document.getElementById('userForm').reset();
        }
        modal.show();
    }

    // Action Functions
    async saveStore() {
        try {
            const formData = new FormData(document.getElementById('storeForm'));
            const data = Object.fromEntries(formData);
            
            const response = await fetch('/api/admin/stores', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            if (result.success) {
                this.showSuccess('매장이 성공적으로 저장되었습니다.');
                bootstrap.Modal.getInstance(document.getElementById('storeModal')).hide();
                this.loadStoresData();
            } else {
                this.showError(result.message || '매장 저장에 실패했습니다.');
            }
        } catch (error) {
            console.error('Failed to save store:', error);
            this.showError('매장 저장 중 오류가 발생했습니다.');
        }
    }

    async saveUser() {
        try {
            const formData = new FormData(document.getElementById('userForm'));
            const data = Object.fromEntries(formData);
            
            const response = await fetch('/api/admin/users', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            if (result.success) {
                this.showSuccess('사용자가 성공적으로 저장되었습니다.');
                bootstrap.Modal.getInstance(document.getElementById('userModal')).hide();
                this.loadUsersData();
            } else {
                this.showError(result.message || '사용자 저장에 실패했습니다.');
            }
        } catch (error) {
            console.error('Failed to save user:', error);
            this.showError('사용자 저장 중 오류가 발생했습니다.');
        }
    }

    async createBackup() {
        try {
            const response = await fetch('/api/admin/backups', {
                method: 'POST'
            });

            const result = await response.json();
            if (result.success) {
                this.showSuccess('백업이 성공적으로 생성되었습니다.');
                this.loadBackupData();
            } else {
                this.showError(result.message || '백업 생성에 실패했습니다.');
            }
        } catch (error) {
            console.error('Failed to create backup:', error);
            this.showError('백업 생성 중 오류가 발생했습니다.');
        }
    }

    // Search and Filter Functions
    performSearch(inputId) {
        const searchTerm = document.getElementById(inputId).value;
        console.log(`Searching for: ${searchTerm} in ${inputId}`);
        // Implement search logic based on current section
    }

    applyFilters() {
        console.log('Applying filters...');
        // Implement filter logic based on current section
    }

    // CRUD Operations
    editStore(storeId) {
        this.showStoreModal(storeId);
    }

    async deleteStore(storeId) {
        if (confirm('정말로 이 매장을 삭제하시겠습니까?')) {
            try {
                const response = await fetch(`/api/admin/stores/${storeId}`, {
                    method: 'DELETE'
                });

                const result = await response.json();
                if (result.success) {
                    this.showSuccess('매장이 성공적으로 삭제되었습니다.');
                    this.loadStoresData();
                } else {
                    this.showError(result.message || '매장 삭제에 실패했습니다.');
                }
            } catch (error) {
                console.error('Failed to delete store:', error);
                this.showError('매장 삭제 중 오류가 발생했습니다.');
            }
        }
    }

    editUser(userId) {
        this.showUserModal(userId);
    }

    async deleteUser(userId) {
        if (confirm('정말로 이 사용자를 삭제하시겠습니까?')) {
            try {
                const response = await fetch(`/api/admin/users/${userId}`, {
                    method: 'DELETE'
                });

                const result = await response.json();
                if (result.success) {
                    this.showSuccess('사용자가 성공적으로 삭제되었습니다.');
                    this.loadUsersData();
                } else {
                    this.showError(result.message || '사용자 삭제에 실패했습니다.');
                }
            } catch (error) {
                console.error('Failed to delete user:', error);
                this.showError('사용자 삭제 중 오류가 발생했습니다.');
            }
        }
    }

    // Placeholder functions for other actions
    viewTicket(ticketId) {
        console.log(`Viewing ticket: ${ticketId}`);
        // Implement ticket view logic
    }

    assignTicket(ticketId) {
        console.log(`Assigning ticket: ${ticketId}`);
        // Implement ticket assignment logic
    }

    downloadBackup(backupId) {
        console.log(`Downloading backup: ${backupId}`);
        // Implement backup download logic
    }

    deleteBackup(backupId) {
        if (confirm('정말로 이 백업을 삭제하시겠습니까?')) {
            console.log(`Deleting backup: ${backupId}`);
            // Implement backup deletion logic
        }
    }

    acknowledgeAlert(alertId) {
        console.log(`Acknowledging alert: ${alertId}`);
        // Implement alert acknowledgment logic
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.adminDashboard = new AdminDashboard();
});

// Global functions for HTML onclick handlers
function showStoreModal() {
    window.adminDashboard.showStoreModal();
}

function showUserModal() {
    window.adminDashboard.showUserModal();
}

function saveStore() {
    window.adminDashboard.saveStore();
}

function saveUser() {
    window.adminDashboard.saveUser();
}

function createBackup() {
    window.adminDashboard.createBackup();
}

function searchStores() {
    window.adminDashboard.performSearch('storeSearchInput');
}

function searchLogs() {
    window.adminDashboard.performSearch('logSearchInput');
}
