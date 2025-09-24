const express = require('express');
const router = express.Router();

// 알림 스트림 엔드포인트 (Server-Sent Events)
router.get('/stream', (req, res) => {
    // SSE 헤더 설정
    res.writeHead(200, {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Cache-Control'
    });

    // 클라이언트 연결 확인
    console.log('📡 알림 스트림 클라이언트 연결됨');

    // 연결 유지를 위한 heartbeat
    const heartbeat = setInterval(() => {
        res.write('data: {"type":"heartbeat","timestamp":' + Date.now() + '}\n\n');
    }, 30000);

    // 연결 종료 처리
    req.on('close', () => {
        console.log('📡 알림 스트림 클라이언트 연결 종료됨');
        clearInterval(heartbeat);
    });

    // 초기 연결 메시지
    res.write('data: {"type":"connected","message":"알림 스트림이 연결되었습니다"}\n\n');
});

// 알림 전송 엔드포인트
router.post('/send', (req, res) => {
    try {
        const { type, message, priority = 'normal', channels = ['websocket'] } = req.body;
        
        // 알림 데이터 생성
        const notification = {
            id: Date.now(),
            type: type || 'general',
            message: message || '새로운 알림이 있습니다',
            priority: priority,
            timestamp: new Date().toISOString(),
            channels: channels
        };

        console.log('📢 알림 전송:', notification);

        // WebSocket으로 브로드캐스트 (실제로는 WebSocket 서버에 전송)
        // 여기서는 간단히 로그만 출력
        res.json({
            success: true,
            message: '알림이 전송되었습니다',
            notification: notification
        });

    } catch (error) {
        console.error('알림 전송 오류:', error);
        res.status(500).json({
            success: false,
            message: '알림 전송에 실패했습니다',
            error: error.message
        });
    }
});

// 알림 히스토리 조회
router.get('/history', (req, res) => {
    try {
        const limit = parseInt(req.query.limit) || 50;
        
        // 임시 히스토리 데이터 (실제로는 데이터베이스에서 조회)
        const history = [
            {
                id: 1,
                type: 'system',
                message: '시스템이 정상적으로 시작되었습니다',
                timestamp: new Date().toISOString(),
                priority: 'normal'
            },
            {
                id: 2,
                type: 'ai',
                message: 'AI 진단이 완료되었습니다',
                timestamp: new Date(Date.now() - 60000).toISOString(),
                priority: 'info'
            }
        ];

        res.json({
            success: true,
            history: history.slice(0, limit),
            total: history.length
        });

    } catch (error) {
        console.error('알림 히스토리 조회 오류:', error);
        res.status(500).json({
            success: false,
            message: '알림 히스토리 조회에 실패했습니다',
            error: error.message
        });
    }
});

// 알림 상태 조회
router.get('/status', (req, res) => {
    res.json({
        success: true,
        status: {
            connected: true,
            channels: ['websocket', 'email', 'sms'],
            last_activity: new Date().toISOString()
        }
    });
});

module.exports = router;
