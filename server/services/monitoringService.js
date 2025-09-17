const EventEmitter = require('events');

class MonitoringService extends EventEmitter {
    constructor() {
        super();
        this.isRunning = false;
    }

    getStatus() {
        return {
            is_running: this.isRunning,
            message: '모니터링 서비스를 구현 중입니다.'
        };
    }
}

module.exports = new MonitoringService();