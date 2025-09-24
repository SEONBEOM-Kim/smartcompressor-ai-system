module.exports = {
  apps: [
    {
      name: 'signalcraft-nodejs',
      script: 'server.js',
      instances: 1, // 안정성을 위해 단일 인스턴스로 시작
      exec_mode: 'fork',
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 4000,
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
    },
    {
      name: 'signalcraft-python',
      script: 'python',
      args: 'app.py',
      interpreter: 'python',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 4000,
      env: {
        FLASK_ENV: 'production',
        FLASK_PORT: 8000
      },
      // 로그 설정
      log_type: 'json',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      error_file: './logs/python_err.log',
      out_file: './logs/python_out.log',
      log_file: './logs/python_combined.log',
      time: true
    }
  ]
};
