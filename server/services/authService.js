class AuthService {
    constructor() {
        this.users = [];
        this.sessions = [];
    }

    async login(email, password) {
        return {
            success: false,
            message: '로그인 기능을 구현 중입니다.'
        };
    }

    async register(userData) {
        return {
            success: false,
            message: '회원가입 기능을 구현 중입니다.'
        };
    }

    async verify(token) {
        return {
            success: false,
            message: '인증 토큰이 필요합니다.'
        };
    }
}

module.exports = new AuthService();