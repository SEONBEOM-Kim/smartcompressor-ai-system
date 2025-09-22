"""
관리자 라우트 - AWS Management Console & GitHub 벤치마킹
서비스 운영 관리 시스템의 API 엔드포인트를 제공합니다.
"""

from flask import Blueprint, jsonify, request, render_template
from admin.services.admin_service import admin_service
from admin.services.store_management_service import store_management_service
from admin.services.user_management_service import user_management_service
from admin.services.monitoring_service import monitoring_service
from admin.services.log_management_service import log_management_service
from admin.services.ticket_system_service import ticket_system_service
from admin.services.security_management_service import security_management_service
from admin.services.backup_management_service import backup_management_service
from admin.services.performance_monitoring_service import performance_monitoring_service
import logging

# Blueprint 생성
admin_bp = Blueprint('admin_bp', __name__, url_prefix='/api/admin')
logger = logging.getLogger(__name__)

# ============================================================================
# 대시보드 및 개요 API
# ============================================================================

@admin_bp.route('/overview', methods=['GET'])
def get_overview():
    """시스템 개요 정보를 조회합니다."""
    try:
        overview_data = admin_service.get_system_overview()
        return jsonify({
            "success": True,
            "data": overview_data
        }), 200
    except Exception as e:
        logger.error(f"Failed to get system overview: {e}")
        return jsonify({
            "success": False,
            "message": "시스템 개요 정보를 가져오는데 실패했습니다."
        }), 500

@admin_bp.route('/dashboard', methods=['GET'])
def admin_dashboard():
    """관리자 대시보드 페이지를 렌더링합니다."""
    return render_template('admin_dashboard.html')

# ============================================================================
# 매장 관리 API
# ============================================================================

@admin_bp.route('/stores', methods=['GET'])
def get_stores():
    """모든 매장 목록을 조회합니다."""
    try:
        stores = store_management_service.get_all_stores()
        return jsonify({
            "success": True,
            "data": stores
        }), 200
    except Exception as e:
        logger.error(f"Failed to get stores: {e}")
        return jsonify({
            "success": False,
            "message": "매장 목록을 가져오는데 실패했습니다."
        }), 500

@admin_bp.route('/stores', methods=['POST'])
def create_store():
    """새 매장을 생성합니다."""
    try:
        data = request.json
        store = store_management_service.create_store(data)
        return jsonify({
            "success": True,
            "data": store,
            "message": "매장이 성공적으로 생성되었습니다."
        }), 201
    except Exception as e:
        logger.error(f"Failed to create store: {e}")
        return jsonify({
            "success": False,
            "message": "매장 생성에 실패했습니다."
        }), 500

@admin_bp.route('/stores/<store_id>', methods=['GET'])
def get_store(store_id):
    """특정 매장 정보를 조회합니다."""
    try:
        store = store_management_service.get_store(store_id)
        if store:
            return jsonify({
                "success": True,
                "data": store
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "매장을 찾을 수 없습니다."
            }), 404
    except Exception as e:
        logger.error(f"Failed to get store {store_id}: {e}")
        return jsonify({
            "success": False,
            "message": "매장 정보를 가져오는데 실패했습니다."
        }), 500

@admin_bp.route('/stores/<store_id>', methods=['PUT'])
def update_store(store_id):
    """매장 정보를 업데이트합니다."""
    try:
        data = request.json
        store = store_management_service.update_store(store_id, data)
        if store:
            return jsonify({
                "success": True,
                "data": store,
                "message": "매장 정보가 성공적으로 업데이트되었습니다."
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "매장을 찾을 수 없습니다."
            }), 404
    except Exception as e:
        logger.error(f"Failed to update store {store_id}: {e}")
        return jsonify({
            "success": False,
            "message": "매장 정보 업데이트에 실패했습니다."
        }), 500

@admin_bp.route('/stores/<store_id>', methods=['DELETE'])
def delete_store(store_id):
    """매장을 삭제합니다."""
    try:
        success = store_management_service.delete_store(store_id)
        if success:
            return jsonify({
                "success": True,
                "message": "매장이 성공적으로 삭제되었습니다."
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "매장을 찾을 수 없습니다."
            }), 404
    except Exception as e:
        logger.error(f"Failed to delete store {store_id}: {e}")
        return jsonify({
            "success": False,
            "message": "매장 삭제에 실패했습니다."
        }), 500

@admin_bp.route('/stores/<store_id>/approve', methods=['POST'])
def approve_store(store_id):
    """매장을 승인합니다."""
    try:
        success = store_management_service.approve_store(store_id)
        if success:
            return jsonify({
                "success": True,
                "message": "매장이 성공적으로 승인되었습니다."
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "매장 승인에 실패했습니다."
            }), 400
    except Exception as e:
        logger.error(f"Failed to approve store {store_id}: {e}")
        return jsonify({
            "success": False,
            "message": "매장 승인 중 오류가 발생했습니다."
        }), 500

@admin_bp.route('/stores/<store_id>/suspend', methods=['POST'])
def suspend_store(store_id):
    """매장을 정지시킵니다."""
    try:
        data = request.json
        reason = data.get('reason', '')
        success = store_management_service.suspend_store(store_id, reason)
        if success:
            return jsonify({
                "success": True,
                "message": "매장이 성공적으로 정지되었습니다."
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "매장 정지에 실패했습니다."
            }), 400
    except Exception as e:
        logger.error(f"Failed to suspend store {store_id}: {e}")
        return jsonify({
            "success": False,
            "message": "매장 정지 중 오류가 발생했습니다."
        }), 500

# ============================================================================
# 사용자 관리 API
# ============================================================================

@admin_bp.route('/users', methods=['GET'])
def get_users():
    """모든 사용자 목록을 조회합니다."""
    try:
        users = user_management_service.get_all_users()
        return jsonify({
            "success": True,
            "data": users
        }), 200
    except Exception as e:
        logger.error(f"Failed to get users: {e}")
        return jsonify({
            "success": False,
            "message": "사용자 목록을 가져오는데 실패했습니다."
        }), 500

@admin_bp.route('/users', methods=['POST'])
def create_user():
    """새 사용자를 생성합니다."""
    try:
        data = request.json
        user = user_management_service.create_user(data)
        return jsonify({
            "success": True,
            "data": user,
            "message": "사용자가 성공적으로 생성되었습니다."
        }), 201
    except Exception as e:
        logger.error(f"Failed to create user: {e}")
        return jsonify({
            "success": False,
            "message": "사용자 생성에 실패했습니다."
        }), 500

@admin_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """특정 사용자 정보를 조회합니다."""
    try:
        user = user_management_service.get_user(user_id)
        if user:
            return jsonify({
                "success": True,
                "data": user
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "사용자를 찾을 수 없습니다."
            }), 404
    except Exception as e:
        logger.error(f"Failed to get user {user_id}: {e}")
        return jsonify({
            "success": False,
            "message": "사용자 정보를 가져오는데 실패했습니다."
        }), 500

@admin_bp.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """사용자 정보를 업데이트합니다."""
    try:
        data = request.json
        user = user_management_service.update_user(user_id, data)
        if user:
            return jsonify({
                "success": True,
                "data": user,
                "message": "사용자 정보가 성공적으로 업데이트되었습니다."
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "사용자를 찾을 수 없습니다."
            }), 404
    except Exception as e:
        logger.error(f"Failed to update user {user_id}: {e}")
        return jsonify({
            "success": False,
            "message": "사용자 정보 업데이트에 실패했습니다."
        }), 500

@admin_bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """사용자를 삭제합니다."""
    try:
        success = user_management_service.delete_user(user_id)
        if success:
            return jsonify({
                "success": True,
                "message": "사용자가 성공적으로 삭제되었습니다."
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "사용자를 찾을 수 없습니다."
            }), 404
    except Exception as e:
        logger.error(f"Failed to delete user {user_id}: {e}")
        return jsonify({
            "success": False,
            "message": "사용자 삭제에 실패했습니다."
        }), 500

@admin_bp.route('/users/<user_id>/permissions', methods=['GET'])
def get_user_permissions(user_id):
    """사용자의 권한을 조회합니다."""
    try:
        permissions = user_management_service.get_user_permissions(user_id)
        return jsonify({
            "success": True,
            "data": permissions
        }), 200
    except Exception as e:
        logger.error(f"Failed to get user permissions {user_id}: {e}")
        return jsonify({
            "success": False,
            "message": "사용자 권한을 가져오는데 실패했습니다."
        }), 500

@admin_bp.route('/users/<user_id>/permissions', methods=['PUT'])
def update_user_permissions(user_id):
    """사용자의 권한을 업데이트합니다."""
    try:
        data = request.json
        permissions = data.get('permissions', [])
        success = user_management_service.update_user_permissions(user_id, permissions)
        if success:
            return jsonify({
                "success": True,
                "message": "사용자 권한이 성공적으로 업데이트되었습니다."
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "사용자 권한 업데이트에 실패했습니다."
            }), 400
    except Exception as e:
        logger.error(f"Failed to update user permissions {user_id}: {e}")
        return jsonify({
            "success": False,
            "message": "사용자 권한 업데이트 중 오류가 발생했습니다."
        }), 500

# ============================================================================
# 서비스 모니터링 API
# ============================================================================

@admin_bp.route('/monitoring', methods=['GET'])
def get_monitoring_data():
    """서비스 모니터링 데이터를 조회합니다."""
    try:
        monitoring_data = monitoring_service.get_monitoring_data()
        return jsonify({
            "success": True,
            "data": monitoring_data
        }), 200
    except Exception as e:
        logger.error(f"Failed to get monitoring data: {e}")
        return jsonify({
            "success": False,
            "message": "모니터링 데이터를 가져오는데 실패했습니다."
        }), 500

@admin_bp.route('/monitoring/services', methods=['GET'])
def get_service_status():
    """서비스 상태를 조회합니다."""
    try:
        services = monitoring_service.get_service_status()
        return jsonify({
            "success": True,
            "data": services
        }), 200
    except Exception as e:
        logger.error(f"Failed to get service status: {e}")
        return jsonify({
            "success": False,
            "message": "서비스 상태를 가져오는데 실패했습니다."
        }), 500

@admin_bp.route('/monitoring/metrics', methods=['GET'])
def get_system_metrics():
    """시스템 메트릭을 조회합니다."""
    try:
        metrics = monitoring_service.get_system_metrics()
        return jsonify({
            "success": True,
            "data": metrics
        }), 200
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        return jsonify({
            "success": False,
            "message": "시스템 메트릭을 가져오는데 실패했습니다."
        }), 500

# ============================================================================
# 로그 관리 API
# ============================================================================

@admin_bp.route('/logs', methods=['GET'])
def get_logs():
    """로그를 조회합니다."""
    try:
        # 쿼리 파라미터에서 필터 정보 추출
        level = request.args.get('level')
        source = request.args.get('source')
        search = request.args.get('search')
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        logs = log_management_service.get_logs(
            level=level,
            source=source,
            search=search,
            start_time=start_time,
            end_time=end_time,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            "success": True,
            "data": logs
        }), 200
    except Exception as e:
        logger.error(f"Failed to get logs: {e}")
        return jsonify({
            "success": False,
            "message": "로그를 가져오는데 실패했습니다."
        }), 500

@admin_bp.route('/logs/export', methods=['POST'])
def export_logs():
    """로그를 내보냅니다."""
    try:
        data = request.json
        filters = data.get('filters', {})
        format_type = data.get('format', 'csv')
        
        export_result = log_management_service.export_logs(filters, format_type)
        if export_result:
            return jsonify({
                "success": True,
                "data": export_result,
                "message": "로그 내보내기가 성공적으로 완료되었습니다."
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "로그 내보내기에 실패했습니다."
            }), 400
    except Exception as e:
        logger.error(f"Failed to export logs: {e}")
        return jsonify({
            "success": False,
            "message": "로그 내보내기 중 오류가 발생했습니다."
        }), 500

@admin_bp.route('/logs/cleanup', methods=['POST'])
def cleanup_logs():
    """오래된 로그를 정리합니다."""
    try:
        data = request.json
        days_to_keep = data.get('days_to_keep', 30)
        
        cleanup_result = log_management_service.cleanup_old_logs(days_to_keep)
        return jsonify({
            "success": True,
            "data": cleanup_result,
            "message": f"{cleanup_result['deleted_count']}개의 오래된 로그가 정리되었습니다."
        }), 200
    except Exception as e:
        logger.error(f"Failed to cleanup logs: {e}")
        return jsonify({
            "success": False,
            "message": "로그 정리 중 오류가 발생했습니다."
        }), 500

# ============================================================================
# 고객 지원 티켓 시스템 API
# ============================================================================

@admin_bp.route('/tickets', methods=['GET'])
def get_tickets():
    """티켓 목록을 조회합니다."""
    try:
        status = request.args.get('status')
        priority = request.args.get('priority')
        assignee = request.args.get('assignee')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        tickets = ticket_system_service.get_tickets(
            status=status,
            priority=priority,
            assignee=assignee,
            page=page,
            per_page=per_page
        )
        
        stats = ticket_system_service.get_ticket_stats()
        
        return jsonify({
            "success": True,
            "data": tickets,
            "stats": stats
        }), 200
    except Exception as e:
        logger.error(f"Failed to get tickets: {e}")
        return jsonify({
            "success": False,
            "message": "티켓 목록을 가져오는데 실패했습니다."
        }), 500

@admin_bp.route('/tickets', methods=['POST'])
def create_ticket():
    """새 티켓을 생성합니다."""
    try:
        data = request.json
        ticket = ticket_system_service.create_ticket(data)
        return jsonify({
            "success": True,
            "data": ticket,
            "message": "티켓이 성공적으로 생성되었습니다."
        }), 201
    except Exception as e:
        logger.error(f"Failed to create ticket: {e}")
        return jsonify({
            "success": False,
            "message": "티켓 생성에 실패했습니다."
        }), 500

@admin_bp.route('/tickets/<ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """특정 티켓을 조회합니다."""
    try:
        ticket = ticket_system_service.get_ticket(ticket_id)
        if ticket:
            return jsonify({
                "success": True,
                "data": ticket
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "티켓을 찾을 수 없습니다."
            }), 404
    except Exception as e:
        logger.error(f"Failed to get ticket {ticket_id}: {e}")
        return jsonify({
            "success": False,
            "message": "티켓 정보를 가져오는데 실패했습니다."
        }), 500

@admin_bp.route('/tickets/<ticket_id>/assign', methods=['POST'])
def assign_ticket(ticket_id):
    """티켓을 담당자에게 할당합니다."""
    try:
        data = request.json
        assignee_id = data.get('assignee_id')
        success = ticket_system_service.assign_ticket(ticket_id, assignee_id)
        if success:
            return jsonify({
                "success": True,
                "message": "티켓이 성공적으로 할당되었습니다."
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "티켓 할당에 실패했습니다."
            }), 400
    except Exception as e:
        logger.error(f"Failed to assign ticket {ticket_id}: {e}")
        return jsonify({
            "success": False,
            "message": "티켓 할당 중 오류가 발생했습니다."
        }), 500

@admin_bp.route('/tickets/<ticket_id>/status', methods=['PUT'])
def update_ticket_status(ticket_id):
    """티켓 상태를 업데이트합니다."""
    try:
        data = request.json
        status = data.get('status')
        comment = data.get('comment', '')
        success = ticket_system_service.update_ticket_status(ticket_id, status, comment)
        if success:
            return jsonify({
                "success": True,
                "message": "티켓 상태가 성공적으로 업데이트되었습니다."
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "티켓 상태 업데이트에 실패했습니다."
            }), 400
    except Exception as e:
        logger.error(f"Failed to update ticket status {ticket_id}: {e}")
        return jsonify({
            "success": False,
            "message": "티켓 상태 업데이트 중 오류가 발생했습니다."
        }), 500

# ============================================================================
# 보안 관리 API
# ============================================================================

@admin_bp.route('/security', methods=['GET'])
def get_security_data():
    """보안 관련 데이터를 조회합니다."""
    try:
        security_data = security_management_service.get_security_overview()
        return jsonify({
            "success": True,
            "data": security_data
        }), 200
    except Exception as e:
        logger.error(f"Failed to get security data: {e}")
        return jsonify({
            "success": False,
            "message": "보안 데이터를 가져오는데 실패했습니다."
        }), 500

@admin_bp.route('/security/events', methods=['GET'])
def get_security_events():
    """보안 이벤트를 조회합니다."""
    try:
        risk_level = request.args.get('risk_level')
        event_type = request.args.get('event_type')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        events = security_management_service.get_security_events(
            risk_level=risk_level,
            event_type=event_type,
            page=page,
            per_page=per_page
        )
        
        return jsonify({
            "success": True,
            "data": events
        }), 200
    except Exception as e:
        logger.error(f"Failed to get security events: {e}")
        return jsonify({
            "success": False,
            "message": "보안 이벤트를 가져오는데 실패했습니다."
        }), 500

@admin_bp.route('/security/blocked-ips', methods=['GET'])
def get_blocked_ips():
    """차단된 IP 목록을 조회합니다."""
    try:
        blocked_ips = security_management_service.get_blocked_ips()
        return jsonify({
            "success": True,
            "data": blocked_ips
        }), 200
    except Exception as e:
        logger.error(f"Failed to get blocked IPs: {e}")
        return jsonify({
            "success": False,
            "message": "차단된 IP 목록을 가져오는데 실패했습니다."
        }), 500

@admin_bp.route('/security/block-ip', methods=['POST'])
def block_ip():
    """IP를 차단합니다."""
    try:
        data = request.json
        ip_address = data.get('ip_address')
        reason = data.get('reason', '')
        duration = data.get('duration', 3600)  # 기본 1시간
        
        success = security_management_service.block_ip(ip_address, reason, duration)
        if success:
            return jsonify({
                "success": True,
                "message": f"IP {ip_address}가 성공적으로 차단되었습니다."
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "IP 차단에 실패했습니다."
            }), 400
    except Exception as e:
        logger.error(f"Failed to block IP: {e}")
        return jsonify({
            "success": False,
            "message": "IP 차단 중 오류가 발생했습니다."
        }), 500

@admin_bp.route('/security/unblock-ip', methods=['POST'])
def unblock_ip():
    """IP 차단을 해제합니다."""
    try:
        data = request.json
        ip_address = data.get('ip_address')
        
        success = security_management_service.unblock_ip(ip_address)
        if success:
            return jsonify({
                "success": True,
                "message": f"IP {ip_address}의 차단이 해제되었습니다."
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "IP 차단 해제에 실패했습니다."
            }), 400
    except Exception as e:
        logger.error(f"Failed to unblock IP: {e}")
        return jsonify({
            "success": False,
            "message": "IP 차단 해제 중 오류가 발생했습니다."
        }), 500

# ============================================================================
# 백업 관리 API
# ============================================================================

@admin_bp.route('/backups', methods=['GET'])
def get_backups():
    """백업 목록을 조회합니다."""
    try:
        backups = backup_management_service.get_backups()
        stats = backup_management_service.get_backup_stats()
        
        return jsonify({
            "success": True,
            "data": backups,
            "stats": stats
        }), 200
    except Exception as e:
        logger.error(f"Failed to get backups: {e}")
        return jsonify({
            "success": False,
            "message": "백업 목록을 가져오는데 실패했습니다."
        }), 500

@admin_bp.route('/backups', methods=['POST'])
def create_backup():
    """새 백업을 생성합니다."""
    try:
        data = request.json
        backup_type = data.get('type', 'full')
        description = data.get('description', '')
        
        backup = backup_management_service.create_backup(backup_type, description)
        return jsonify({
            "success": True,
            "data": backup,
            "message": "백업이 성공적으로 생성되었습니다."
        }), 201
    except Exception as e:
        logger.error(f"Failed to create backup: {e}")
        return jsonify({
            "success": False,
            "message": "백업 생성에 실패했습니다."
        }), 500

@admin_bp.route('/backups/<backup_id>/download', methods=['GET'])
def download_backup(backup_id):
    """백업을 다운로드합니다."""
    try:
        download_url = backup_management_service.get_backup_download_url(backup_id)
        if download_url:
            return jsonify({
                "success": True,
                "data": {"download_url": download_url}
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "백업 다운로드 URL을 생성할 수 없습니다."
            }), 400
    except Exception as e:
        logger.error(f"Failed to get backup download URL {backup_id}: {e}")
        return jsonify({
            "success": False,
            "message": "백업 다운로드 URL 생성 중 오류가 발생했습니다."
        }), 500

@admin_bp.route('/backups/<backup_id>', methods=['DELETE'])
def delete_backup(backup_id):
    """백업을 삭제합니다."""
    try:
        success = backup_management_service.delete_backup(backup_id)
        if success:
            return jsonify({
                "success": True,
                "message": "백업이 성공적으로 삭제되었습니다."
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "백업 삭제에 실패했습니다."
            }), 400
    except Exception as e:
        logger.error(f"Failed to delete backup {backup_id}: {e}")
        return jsonify({
            "success": False,
            "message": "백업 삭제 중 오류가 발생했습니다."
        }), 500

@admin_bp.route('/backups/<backup_id>/restore', methods=['POST'])
def restore_backup(backup_id):
    """백업을 복원합니다."""
    try:
        data = request.json
        target_environment = data.get('target_environment', 'production')
        
        restore_result = backup_management_service.restore_backup(backup_id, target_environment)
        if restore_result:
            return jsonify({
                "success": True,
                "data": restore_result,
                "message": "백업 복원이 시작되었습니다."
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "백업 복원에 실패했습니다."
            }), 400
    except Exception as e:
        logger.error(f"Failed to restore backup {backup_id}: {e}")
        return jsonify({
            "success": False,
            "message": "백업 복원 중 오류가 발생했습니다."
        }), 500

# ============================================================================
# 성능 모니터링 API
# ============================================================================

@admin_bp.route('/performance', methods=['GET'])
def get_performance_data():
    """성능 모니터링 데이터를 조회합니다."""
    try:
        performance_data = performance_monitoring_service.get_performance_data()
        return jsonify({
            "success": True,
            "data": performance_data
        }), 200
    except Exception as e:
        logger.error(f"Failed to get performance data: {e}")
        return jsonify({
            "success": False,
            "message": "성능 데이터를 가져오는데 실패했습니다."
        }), 500

@admin_bp.route('/performance/metrics', methods=['GET'])
def get_performance_metrics():
    """성능 메트릭을 조회합니다."""
    try:
        time_range = request.args.get('time_range', '24h')
        metrics = performance_monitoring_service.get_performance_metrics(time_range)
        return jsonify({
            "success": True,
            "data": metrics
        }), 200
    except Exception as e:
        logger.error(f"Failed to get performance metrics: {e}")
        return jsonify({
            "success": False,
            "message": "성능 메트릭을 가져오는데 실패했습니다."
        }), 500

@admin_bp.route('/performance/alerts', methods=['GET'])
def get_performance_alerts():
    """성능 알림을 조회합니다."""
    try:
        alerts = performance_monitoring_service.get_performance_alerts()
        return jsonify({
            "success": True,
            "data": alerts
        }), 200
    except Exception as e:
        logger.error(f"Failed to get performance alerts: {e}")
        return jsonify({
            "success": False,
            "message": "성능 알림을 가져오는데 실패했습니다."
        }), 500

@admin_bp.route('/performance/alerts/<alert_id>/acknowledge', methods=['POST'])
def acknowledge_performance_alert(alert_id):
    """성능 알림을 확인 처리합니다."""
    try:
        success = performance_monitoring_service.acknowledge_alert(alert_id)
        if success:
            return jsonify({
                "success": True,
                "message": "알림이 확인 처리되었습니다."
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "알림 확인 처리에 실패했습니다."
            }), 400
    except Exception as e:
        logger.error(f"Failed to acknowledge alert {alert_id}: {e}")
        return jsonify({
            "success": False,
            "message": "알림 확인 처리 중 오류가 발생했습니다."
        }), 500

# ============================================================================
# 에러 핸들러
# ============================================================================

@admin_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "message": "요청한 리소스를 찾을 수 없습니다."
    }), 404

@admin_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        "success": False,
        "message": "서버 내부 오류가 발생했습니다."
    }), 500