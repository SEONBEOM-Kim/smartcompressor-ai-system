const database = require('../config/database');

// 인증 미들웨어
function authenticateToken(req, res, next) {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];
    
    if (!token) {
        return res.status(401).json({ 
            success: false, 
            message: '인증 토큰이 필요합니다.' 
        });
    }
    
    const session = database.getSession(token);
    if (!session) {
        return res.status(401).json({ 
            success: false, 
            message: '유효하지 않은 토큰입니다.' 
        });
    }
    
    req.user = session;
    next();
}

// 관리자 권한 확인 미들웨어
function requireAdmin(req, res, next) {
    if (!req.user || req.user.role !== 'admin') {
        return res.status(403).json({
            success: false,
            message: '관리자 권한이 필요합니다.'
        });
    }
    next();
}

module.exports = {
    authenticateToken,
    requireAdmin
};
