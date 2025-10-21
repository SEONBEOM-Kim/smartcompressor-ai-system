// static/js/dashboard/charts/power-chart.js
class PowerChart {
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
                        label: '전력 소비 (%)',
                        data: [],
                        backgroundColor: '#36b9cc',
                        borderColor: '#36b9cc',
                        borderWidth: 1
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

    update(data) {
        if (this.chart && data) {
            this.chart.data.labels = data.labels || [];
            this.chart.data.datasets[0].data = data.values || [];
            this.chart.update();
        }
    }
}