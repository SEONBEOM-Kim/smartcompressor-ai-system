const app = require('./server/app');
const WebSocketService = require('./server/services/websocketService');
const monitoringService = require('./server/services/monitoringService');
const PORT = process.env.PORT || 3000;

// 서버 시작
const server = app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Signalcraft 리팩토링된 서버가 http://0.0.0.0:${PORT} 에서 실행 중입니다`);
    console.log(`🌐 외부 접근: http://signalcraft.kr:${PORT}`);
    console.log(`📁 정적 파일 서빙: static/ 폴더`);
    console.log(`🔗 API 엔드포인트: /api/*`);
    console.log(`👨‍💼 관리자 대시보드: /admin`);
    console.log(`🧠 AI 진단: /api/ai/*`);
    console.log(`📊 실시간 모니터링: /api/monitoring/*`);
    console.log(`🔌 웹소켓: 실시간 알림 지원`);
    console.log(`⏰ 시작 시간: ${new Date().toISOString()}`);
    console.log(`💾 메모리 최적화: 모듈화 완료`);
});

// 웹소켓 서비스 초기화
const wsService = new WebSocketService(server);

// 모니터링 서비스와 웹소켓 연동
monitoringService.on('alert', (alert) => {
    wsService.broadcastAlert(alert);
});

monitoringService.on('statusUpdate', (status) => {
    wsService.broadcastMonitoringStatus(status);
});

monitoringService.on('statsUpdate', (stats) => {
    wsService.broadcastMonitoringStats(stats);
});

// 에러 처리
process.on('uncaughtException', (err) => {
    console.error('Uncaught Exception:', err);
    process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
    process.exit(1);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down gracefully');
    server.close(() => {
        console.log('Process terminated');
        process.exit(0);
    });
});

process.on('SIGINT', () => {
    console.log('SIGINT received, shutting down gracefully');
    server.close(() => {
        console.log('Process terminated');
        process.exit(0);
    });
});