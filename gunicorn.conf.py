# Gunicorn configuration file for SignalCraft Flask application
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"  # 기존 포트 유지 (기존 8000)
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Restart settings
max_worker_connections = 1000

# Logging
accesslog = "-"  # stdout로 로그 출력
errorlog = "-"   # stdout로 오류 로그 출력
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'signalcraft-gunicorn'

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190