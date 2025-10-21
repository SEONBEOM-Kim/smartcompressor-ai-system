// static/js/dashboard/charts/device-status-chart.js
class DeviceStatusChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.chart = null;
        this.init();
    }

    init() {
        if (this.canvas) {
            this.chart = new Chart(this.canvas, {
                type: 'doughnut',
                data: {
                    labels: ['온라인', '오프라인', '점검중', '오류'],
                    datasets: [{
                        data: [0, 0, 0, 0],
                        backgroundColor: ['#1cc88a', '#e74a3b', '#36b9cc', '#f6c23e'],
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
    }

    update(data) {
        if (this.chart && data) {
            this.chart.data.datasets[0].data = [
                data.online || 0,
                data.offline || 0,
                data.maintenance || 0,
                data.error || 0
            ];
            this.chart.update();
        }
    }
}