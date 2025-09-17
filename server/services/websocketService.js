class WebSocketService {
    constructor(server) {
        this.server = server;
        console.log('웹소켓 서비스가 초기화되었습니다.');
    }

    broadcastAlert(alert) {
        console.log('알림 브로드캐스트:', alert);
    }

    broadcastMonitoringStatus(status) {
        console.log('모니터링 상태 브로드캐스트:', status);
    }

    broadcastMonitoringStats(stats) {
        console.log('모니터링 통계 브로드캐스트:', stats);
    }
}

module.exports = WebSocketService;