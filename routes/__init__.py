from .auth_routes import auth_bp
from .admin_routes import admin_bp
from .payment_routes import payment_bp
from .main_routes import main_bp

__all__ = ['auth_bp', 'admin_bp', 'payment_bp', 'main_bp']
