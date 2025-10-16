// static/js/dashboard/ui/table-renderer.js
import { getStatusClass as getStatusClassFmt, getStatusText as getStatusTextFmt, 
         getHealthClass as getHealthClassFmt, getPriorityClass as getPriorityClassFmt, 
         formatDate as formatDateFmt } 
         from '../../common/utils/formatters.js';

class TableRenderer {
    updateStoresTable(stores) {
        const tbody = document.getElementById('storesTableBody');
        if (!tbody) return;

        tbody.innerHTML = '';

        stores.forEach(store => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${store.store_name}</td>
                <td>${store.address}</td>
                <td><span class="badge badge-${this.getStatusClass(store.status)}">${this.getStatusText(store.status)}</span></td>
                <td>${store.total_devices || 0}</td>
                <td>
                    <div class="progress">
                        <div class="progress-bar" style="width: ${store.uptime_percentage || 0}%"></div>
                    </div>
                    <small>${(store.uptime_percentage || 0).toFixed(1)}%</small>
                </td>
                <td>${this.formatDate(store.last_activity)}</td>
                <td>
                    <button class="btn btn-sm btn-primary me-1" onclick="editStore('${store.store_id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteStore('${store.store_id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    updateDevicesTable(devices) {
        const tbody = document.getElementById('devicesTableBody');
        if (!tbody) return;

        tbody.innerHTML = '';

        devices.forEach(device => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${device.device_name}</td>
                <td>${device.store_name || 'N/A'}</td>
                <td>${device.device_type}</td>
                <td><span class="badge badge-${this.getStatusClass(device.status)}">${this.getStatusText(device.status)}</span></td>
                <td>
                    <span class="health-score ${this.getHealthClass(device.health_score)}">
                        ${(device.health_score || 0).toFixed(1)}%
                    </span>
                </td>
                <td>${this.formatDate(device.last_maintenance)}</td>
                <td>
                    <button class="btn btn-sm btn-primary me-1" onclick="editDevice('${device.device_id}')">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteDevice('${device.device_id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    updateNotificationsTable(notifications) {
        const tbody = document.getElementById('notificationsTableBody');
        if (!tbody) return;

        tbody.innerHTML = '';

        notifications.forEach(notification => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${this.formatDate(notification.created_at)}</td>
                <td><span class="badge badge-${this.getPriorityClass(notification.priority)}">${notification.event_type}</span></td>
                <td>${notification.store_name || 'N/A'}</td>
                <td>${notification.message}</td>
                <td><span class="badge badge-${this.getStatusClass(notification.status)}">${this.getStatusText(notification.status)}</span></td>
            `;
            tbody.appendChild(row);
        });
    }

    getStatusClass(status) {
        return getStatusClassFmt(status);
    }

    getStatusText(status) {
        return getStatusTextFmt(status);
    }

    getHealthClass(score) {
        return getHealthClassFmt(score);
    }

    getPriorityClass(priority) {
        return getPriorityClassFmt(priority);
    }

    formatDate(dateString) {
        return formatDateFmt(dateString);
    }
}