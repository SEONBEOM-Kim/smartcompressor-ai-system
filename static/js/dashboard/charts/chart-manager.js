// static/js/dashboard/charts/chart-manager.js
class ChartManager {
    constructor() {
        this.charts = {};
    }

    initializeAllCharts() {
        this.charts.energy = new EnergyChart('energyChart');
        this.charts.deviceStatus = new DeviceStatusChart('deviceStatusChart');
        this.charts.temperature = new TemperatureChart('temperatureChart');
        this.charts.vibration = new VibrationChart('vibrationChart');
        this.charts.power = new PowerChart('powerChart');
        this.charts.anomaly = new AnomalyChart('anomalyChart');
    }
}