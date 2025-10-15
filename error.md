PS C:\Users\gmdqn\signalcraft> node server.js
[dotenv@17.2.2] injecting env (12) from .env -- tip: 🛠️  run anywhere with `dotenvx ruun -- yourcommand`
웹소켓 서비스가 초기화되었습니다.
🚀 Signalcraft 리팩토링된 서버가 http://0.0.0.0:3000 에서 실행 중입니다
🌐 외부 접근: http://signalcraft.kr:3000
📁 정적 파일 서빙: static/ 폴더
🔗 API 엔드포인트: /api/*
👨‍💼 관리자 대시보드: /admin
🧠 AI 진단: /api/ai/*
📊 실시간 모니터링: /api/monitoring/*
🔌 웹소켓: 실시간 알림 지원
⏰ 시작 시간: 2025-10-15T06:42:53.040Z
💾 메모리 최적화: 모듈화 완료
✅ SQLite 데이터베이스 연결 성공: C:\Users\gmdqn\signalcraft\database\smartcompressor.db
✅ SQLite 데이터베이스 연결 성공: C:\Users\gmdqn\signalcraft\database\smartcompressor.db
✅ users 테이블 생성 완료
✅ users 테이블 생성 완료
✅ sessions 테이블 생성 완료
✅ sessions 테이블 생성 완료
✅ 인덱스 생성 완료
✅ 인덱스 생성 완료
데이터베이스 초기화 실패: Error: Connection terminated due to connection timeout
    at C:\Users\gmdqn\signalcraft\node_modules\pg-pool\index.js:45:11
    at process.processTicksAndRejections (node:internal/process/task_queues:105:5)    
    at async DatabaseService.createTables (C:\Users\gmdqn\signalcraft\services\database_service.js:38:24)
    at async DatabaseService.init (C:\Users\gmdqn\signalcraft\services\database_service.js:30:13) {
  [cause]: Error: Connection terminated unexpectedly
      at Connection.<anonymous> (C:\Users\gmdqn\signalcraft\node_modules\pg\lib\client.js:136:73)
      at Object.onceWrapper (node:events:632:28)
      at Connection.emit (node:events:518:28)
      at Connection.emit (node:domain:489:12)
      at Socket.<anonymous> (C:\Users\gmdqn\signalcraft\node_modules\pg\lib\connection.js:62:12)
      at Socket.emit (node:events:518:28)
      at Socket.emit (node:domain:489:12)
      at TCP.<anonymous> (node:net:351:12)
}
데이터베이스 초기화 실패: Error: Connection terminated due to connection timeout
    at C:\Users\gmdqn\signalcraft\node_modules\pg-pool\index.js:45:11
    at process.processTicksAndRejections (node:internal/process/task_queues:105:5)    
    at async DatabaseService.createTables (C:\Users\gmdqn\signalcraft\services\database_service.js:38:24)
    at async DatabaseService.init (C:\Users\gmdqn\signalcraft\services\database_service.js:30:13) {
  [cause]: Error: Connection terminated unexpectedly
      at Connection.<anonymous> (C:\Users\gmdqn\signalcraft\node_modules\pg\lib\client.js:136:73)
      at Object.onceWrapper (node:events:632:28)
      at Connection.emit (node:events:518:28)
      at Connection.emit (node:domain:489:12)
      at Socket.<anonymous> (C:\Users\gmdqn\signalcraft\node_modules\pg\lib\connection.js:62:12)
      at Socket.emit (node:events:518:28)
      at Socket.emit (node:domain:489:12)
      at TCP.<anonymous> (node:net:351:12)
}
