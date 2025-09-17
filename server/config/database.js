// 메모리 기반 데이터 저장소 (실제로는 데이터베이스 사용)
class MemoryDatabase {
    constructor() {
        this.users = [
            {
                id: 1,
                email: 'admin@signalcraft.kr',
                password: 'admin123!',
                name: '관리자',
                company: 'Signalcraft',
                role: 'admin',
                created_at: new Date().toISOString()
            }
        ];
        this.sessions = {};
        this.diagnosisHistory = [];
    }

    // 사용자 관련 메서드
    findUserByEmail(email) {
        return this.users.find(u => u.email === email);
    }

    findUserById(id) {
        return this.users.find(u => u.id === id);
    }

    getUserById(id) {
        return this.users.find(u => u.id === id);
    }

    createUser(userData) {
        const newUser = {
            id: this.users.length + 1,
            ...userData,
            created_at: new Date().toISOString()
        };
        this.users.push(newUser);
        return newUser;
    }

    // 세션 관련 메서드
    createSession(userId, userData) {
        const sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        this.sessions[sessionId] = {
            userId,
            ...userData,
            createdAt: new Date().toISOString()
        };
        return sessionId;
    }

    getSession(sessionId) {
        return this.sessions[sessionId];
    }

    deleteSession(sessionId) {
        delete this.sessions[sessionId];
    }

    // 진단 기록 관련 메서드
    addDiagnosisRecord(record) {
        this.diagnosisHistory.push({
            id: this.diagnosisHistory.length + 1,
            ...record,
            timestamp: new Date().toISOString()
        });
    }

    getDiagnosisHistory(limit = 100) {
        return this.diagnosisHistory.slice(-limit);
    }

    // 메모리 정리 (오래된 세션 삭제)
    cleanup() {
        const now = Date.now();
        const maxAge = 24 * 60 * 60 * 1000; // 24시간

        Object.keys(this.sessions).forEach(sessionId => {
            const session = this.sessions[sessionId];
            const sessionAge = now - new Date(session.createdAt).getTime();
            
            if (sessionAge > maxAge) {
                delete this.sessions[sessionId];
            }
        });
    }
}

// 싱글톤 인스턴스
const database = new MemoryDatabase();

// 주기적으로 메모리 정리 (5분마다)
setInterval(() => {
    database.cleanup();
}, 5 * 60 * 1000);

module.exports = database;
