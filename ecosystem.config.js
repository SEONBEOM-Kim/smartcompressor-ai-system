module.exports = {
  apps: [
    {
      name: 'signalcraft-nodejs',
      script: 'server.js',
      instances: 'max', // 클러스터 모드를 사용하여 CPU 코어 수만큼 인스턴스 생성
      exec_mode: 'cluster', // fork → cluster 모드로 변경하여 다중 인스턴스 처리
      autorestart: true,
      watch: false,
      max_memory_restart: '1G', // 메모리 제한 증가
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
      error_file: './logs/nodejs_error.log',
      out_file: './logs/nodejs_out.log',
      log_file: './logs/nodejs_combined.log',
      time: true,
      // 로그 로테이션
      log_rotate: true,
      max_log_size: '10M',
      retain_logs: 7
    },
    {
      name: 'signalcraft-python',
      script: 'gunicorn',
      args: '-c gunicorn.conf.py app:app',
      interpreter: 'python3',
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        FLASK_ENV: 'development',
        PYTHONPATH: '.'
      },
      env_production: {
        FLASK_ENV: 'production',
        PYTHONPATH: '.'
      },
      // 로그 설정
      log_type: 'json',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      error_file: './logs/python_error.log',
      out_file: './logs/python_out.log',
      log_file: './logs/python_combined.log',
      time: true,
      // 로그 로테이션
      log_rotate: true,
      max_log_size: '10M',
      retain_logs: 7
    }
  ]
};
