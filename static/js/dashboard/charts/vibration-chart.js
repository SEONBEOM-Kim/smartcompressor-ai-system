// static/js/dashboard/charts/vibration-chart.js
class VibrationChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.chart = null;
        this.init();
    }

    init() {
        if (this.canvas) {
            this.chart = new Chart(this.canvas, {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{
                        label: '진동 레벨 (g)',
                        data: [],
                        backgroundColor: '#f6c23e',
                        borderColor: '#f6c23e',
                        borderWidth: 1
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

    update(data) {
        if (this.chart && data) {
            this.chart.data.labels = data.labels || [];
            this.chart.data.datasets[0].data = data.values || [];
            this.chart.update();
        }
    }
}