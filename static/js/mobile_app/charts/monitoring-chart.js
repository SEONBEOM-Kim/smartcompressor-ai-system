class MonitoringChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.chart = null;
    }

    init() {
        if (!this.canvas) return;

        this.chart = new Chart(this.canvas, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: '온도',
                    data: [],
                    borderColor: '#00D4AA',
                    backgroundColor: 'rgba(0, 212, 170, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        display: false
                    },
                    y: {
                        display: false
                    }
                },
                elements: {
                    point: {
                        radius: 0
                    }
                }
            }
        });
    }

    updateMonitoringData() {
        if (!this.chart) return;

        const now = new Date();
        const timeLabel = now.toLocaleTimeString('ko-KR', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });

        const newValue = Math.random() * 100;

        this.chart.data.labels.push(timeLabel);
        this.chart.data.datasets[0].data.push(newValue);

        if (this.chart.data.labels.length > 20) {
            this.chart.data.labels.shift();
            this.chart.data.datasets[0].data.shift();
        }

        this.chart.update('none');
    }

    switchMonitoringType(type) {
        document.querySelectorAll('.control-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-type="${type}"]`).classList.add('active');

        let color, label;
        switch (type) {
            case 'temperature':
                color = '#00D4AA';
                label = '온도';
                break;
            case 'efficiency':
                color = '#007AFF';
                label = '효율성';
                break;
            case 'power':
                color = '#FF9500';
                label = '전력';
                break;
        }

        this.chart.data.datasets[0].label = label;
        this.chart.data.datasets[0].borderColor = color;
        this.chart.data.datasets[0].backgroundColor = color + '20';
        this.chart.update();
    }
}

export default MonitoringChart;