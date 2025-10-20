// static/js/dashboard/reports/reports-chart.js
class ReportsChart {
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
                    labels: ['베어링 마모 의심', '과도한 진동', '온도 급상승', '기타'],
                    datasets: [{
                        label: '징후 유형',
                        data: [12, 9, 6, 3],
                        backgroundColor: [
                            '#e74c3c',
                            '#f39c12',
                            '#8259de',
                            '#3498db'
                        ],
                        borderColor: '#2c2c54',
                        borderWidth: 4
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#e0e0e0'
                            }
                        },
                        title: {
                            display: true,
                            text: '징후 유형별 분포',
                            color: '#ffffff'
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