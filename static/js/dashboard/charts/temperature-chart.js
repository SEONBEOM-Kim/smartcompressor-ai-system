// static/js/dashboard/charts/temperature-chart.js
class TemperatureChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.chart = null;
        this.init();
    }

    init() {
        if (this.canvas) {
            this.chart = new Chart(this.canvas, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: '온도 (°C)',
                        data: [],
                        borderColor: '#e74a3b',
                        backgroundColor: 'rgba(231, 74, 59, 0.1)',
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: false
                        }
                    }
                }
            });
        }
    }

    update(data) {
        if (this.chart && data) {
            this.chart.data.labels = data.labels || [];
            this.chart.data.datasets[0].data = data.values || [];
            this.chart.update();
        }
    }
}