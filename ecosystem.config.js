module.exports = {
  apps: [
    {
      name: 'signalcraft-nodejs',
      script: 'server.js',
      instances: 1, // 안정성을 위해 단일 인스턴스로 시작
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '512M', // 메모리 제한을 더 낮게 설정
      min_uptime: '30s', // 최소 실행 시간 증가
      max_restarts: 5, // 재시작 횟수 제한
      restart_delay: 10000, // 재시작 지연 시간 증가
      kill_timeout: 5000, // 강제 종료 타임아웃
      wait_ready: true, // 준비 완료 대기
      env: {
        NODE_ENV: 'development',
        PORT: 3000
      },
      env_production: {
        NODE_ENV: 'production',
        PORT: 3000
      },
      // 로그 설정
      log_type: 'json',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      error_file: './logs/err.log',
      out_file: './logs/out.log',
      log_file: './logs/combined.log',
      time: true,
      // 로그 로테이션
      log_rotate: true,
      max_log_size: '10M',
      retain_logs: 7
    }
  ]
};
