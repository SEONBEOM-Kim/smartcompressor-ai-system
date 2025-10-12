class DashboardUpdater {
    updateDashboardUI(data) {
        if (data.compressor_status) {
            this.updateCompressorStatus(data.compressor_status);
        }
        if (data.realtime_data) {
            this.updateRealtimeData(data.realtime_data);
        }
        if (data.payment_summary) {
            this.updatePaymentSummary(data.payment_summary);
        }
    }

    updateCompressorStatus(status) {
        const statusBadge = document.getElementById('compressorStatusBadge');
        const statusText = statusBadge?.querySelector('.status-text');
        const statusIndicator = statusBadge?.querySelector('.status-indicator');

        if (statusText && statusIndicator) {
            statusText.textContent = status.status;
            statusIndicator.className = `status-indicator ${status.status.toLowerCase()}`;
        }

        // 상태별 색상 적용
        if (status.status === '정상') {
            statusIndicator.style.background = 'var(--status-normal)';
        } else if (status.status === '경고') {
            statusIndicator.style.background = 'var(--status-warning)';
        } else if (status.status === '이상') {
            statusIndicator.style.background = 'var(--status-error)';
        }
    }

    updateRealtimeData(data) {
        const tempElement = document.getElementById('temperatureValue');
        if (tempElement && data.temperature) {
            tempElement.textContent = `${data.temperature}°C`;
        }

        const efficiencyElement = document.getElementById('efficiencyValue');
        if (efficiencyElement && data.efficiency) {
            efficiencyElement.textContent = `${Math.round(data.efficiency * 100)}%`;
        }

        const powerElement = document.getElementById('powerValue');
        if (powerElement && data.power_consumption) {
            powerElement.textContent = `${data.power_consumption}W`;
        }

        const vibrationElement = document.getElementById('vibrationValue');
        if (vibrationElement && data.vibration) {
            vibrationElement.textContent = data.vibration;
        }
    }

    updatePaymentSummary(summary) {
        const todayRevenue = document.getElementById('todayRevenue');
        if (todayRevenue && summary.today_revenue) {
            todayRevenue.textContent = `₩${summary.today_revenue.toLocaleString()}`;
        }

        const transactionCount = document.getElementById('transactionCount');
        if (transactionCount && summary.transaction_count) {
            transactionCount.textContent = `${summary.transaction_count}건`;
        }

        const averagePayment = document.getElementById('averagePayment');
        if (averagePayment && summary.average_payment) {
            averagePayment.textContent = `₩${Math.round(summary.average_payment).toLocaleString()}`;
        }
    }
}

export default DashboardUpdater;