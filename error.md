venv) ubuntu@ip-172-31-33-230:~/smartcompressor-ai-system$ nano .env

(venv) ubuntu@ip-172-31-33-230:~/smartcompressor-ai-system$ pm2 start server.js --name signalcraft-app

[PM2] Spawning PM2 daemon with pm2_home=/home/ubuntu/.pm2

[PM2] PM2 Successfully daemonized

[PM2] Starting /home/ubuntu/smartcompressor-ai-system/server.js in fork_mode (1 instance)

[PM2] Done.

┌────┬────────────────────┬──────────┬──────┬───────────┬──────────┬──────────┐

│ id │ name               │ mode     │ ↺    │ status    │ cpu      │ memory   │

├────┼────────────────────┼──────────┼──────┼───────────┼──────────┼──────────┤

│ 0  │ signalcraft-app    │ fork     │ 0    │ online    │ 0%       │ 37.5mb   │

└────┴────────────────────┴──────────┴──────┴───────────┴──────────┴──────────┘

(venv) ubuntu@ip-172-31-33-230:~/smartcompressor-ai-system$ pm2 logs

[TAILING] Tailing last 15 lines for [all] processes (change the value with --lines option)

/home/ubuntu/.pm2/pm2.log last 15 lines:

PM2        | 2025-10-15T07:42:31: PM2 log: Node.js version      : 18.20.8

PM2        | 2025-10-15T07:42:31: PM2 log: Current arch         : x64

PM2        | 2025-10-15T07:42:31: PM2 log: PM2 home             : /home/ubuntu/.pm2

PM2        | 2025-10-15T07:42:31: PM2 log: PM2 PID file         : /home/ubuntu/.pm2/pm2.pid

PM2        | 2025-10-15T07:42:31: PM2 log: RPC socket file      : /home/ubuntu/.pm2/rpc.sock

PM2        | 2025-10-15T07:42:31: PM2 log: BUS socket file      : /home/ubuntu/.pm2/pub.sock

PM2        | 2025-10-15T07:42:31: PM2 log: Application log path : /home/ubuntu/.pm2/logs

PM2        | 2025-10-15T07:42:31: PM2 log: Worker Interval      : 30000

PM2        | 2025-10-15T07:42:31: PM2 log: Process dump file    : /home/ubuntu/.pm2/dump.pm2

PM2        | 2025-10-15T07:42:31: PM2 log: Concurrent actions   : 2

PM2        | 2025-10-15T07:42:31: PM2 log: SIGTERM timeout      : 1600

PM2        | 2025-10-15T07:42:31: PM2 log: Runtime Binary       : /usr/bin/node

PM2        | 2025-10-15T07:42:31: PM2 log: ===============================================================================

PM2        | 2025-10-15T07:42:31: PM2 log: App [signalcraft-app:0] starting in -fork mode-

PM2        | 2025-10-15T07:42:31: PM2 log: App [signalcraft-app:0] online



/home/ubuntu/.pm2/logs/signalcraft-app-out.log last 15 lines:

0|signalcr | 🔗 API 엔드포인트: /api/*

0|signalcr | 👨‍💼 관리자 대시보드: /admin

0|signalcr | 🧠 AI 진단: /api/ai/*

0|signalcr | 📊 실시간 모니터링: /api/monitoring/*

0|signalcr | 🔌 웹소켓: 실시간 알림 지원

0|signalcr | ⏰ 시작 시간: 2025-10-15T07:42:32.534Z

0|signalcr | 💾 메모리 최적화: 모듈화 완료

0|signalcr | ✅ SQLite 데이터베이스 연결 성공: /home/ubuntu/smartcompressor-ai-system/database/smartcompressor.db

0|signalcr | ✅ SQLite 데이터베이스 연결 성공: /home/ubuntu/smartcompressor-ai-system/database/smartcompressor.db

0|signalcr | ✅ users 테이블 생성 완료

0|signalcr | ✅ sessions 테이블 생성 완료

0|signalcr | ✅ 인덱스 생성 완료

0|signalcr | ✅ users 테이블 생성 완료

0|signalcr | ✅ sessions 테이블 생성 완료

0|signalcr | ✅ 인덱스 생성 완료



/home/ubuntu/.pm2/logs/signalcraft-app-error.log last 15 lines:

0|signalcr | 데이터베이스 초기화 실패: Error: Connection terminated due to connection timeout

0|signalcr |     at /home/ubuntu/smartcompressor-ai-system/node_modules/pg-pool/index.js:45:11

0|signalcr |     at process.processTicksAndRejections (node:internal/process/task_queues:95:5)

0|signalcr |     at async DatabaseService.createTables (/home/ubuntu/smartcompressor-ai-system/services/database_service.js:38:24)

0|signalcr |     at async DatabaseService.init (/home/ubuntu/smartcompressor-ai-system/services/database_service.js:30:13) {

0|signalcr |   [cause]: Error: Connection terminated unexpectedly

0|signalcr |       at Connection.<anonymous> (/home/ubuntu/smartcompressor-ai-system/node_modules/pg/lib/client.js:136:73)

0|signalcr |       at Object.onceWrapper (node:events:631:28)

0|signalcr |       at Connection.emit (node:events:517:28)

0|signalcr |       at Connection.emit (node:domain:489:12)

0|signalcr |       at Socket.<anonymous> (/home/ubuntu/smartcompressor-ai-system/node_modules/pg/lib/connection.js:62:12)

0|signalcr |       at Socket.emit (node:events:517:28)

0|signalcr |       at Socket.emit (node:domain:489:12)

0|signalcr |       at TCP.<anonymous> (node:net:350:12)

0|signalcr | }