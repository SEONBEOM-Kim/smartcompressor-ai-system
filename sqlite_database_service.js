/**
 * SQLite 데이터베이스 서비스
 * 배포 환경에서 사용할 수 있는 안정적인 데이터베이스 관리
 */

const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

class SQLiteDatabaseService {
    constructor() {
        // 데이터베이스 파일 경로 (프로젝트 루트에 저장)
        this.dbPath = path.join(__dirname, '..', 'database', 'smartcompressor.db');
        this.db = null;
        
        // 데이터베이스 디렉토리 생성
        this.ensureDatabaseDir();
        
        this.init();
    }

    ensureDatabaseDir() {
        const dbDir = path.dirname(this.dbPath);
        if (!fs.existsSync(dbDir)) {
            fs.mkdirSync(dbDir, { recursive: true });
            console.log('📁 데이터베이스 디렉토리 생성:', dbDir);
        }
    }

    async init() {
        return new Promise((resolve, reject) => {
            this.db = new sqlite3.Database(this.dbPath, (err) => {
                if (err) {
                    console.error('❌ SQLite 데이터베이스 연결 실패:', err);
                    reject(err);
                } else {
                    console.log('✅ SQLite 데이터베이스 연결 성공:', this.dbPath);
                    this.createTables().then(resolve).catch(reject);
                }
            });
        });
    }

    async createTables() {
        return new Promise((resolve, reject) => {
            const createUsersTable = `
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100),
                    phone VARCHAR(20),
                    role VARCHAR(20) DEFAULT 'user',
                    additional_info TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME
                )
            `;

            const createSessionsTable = `
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id VARCHAR(255) UNIQUE NOT NULL,
                    user_id INTEGER NOT NULL,
                    expires_at DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            `;

            const createIndexes = `
                CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
                CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON sessions(session_id);
                CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
                CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
            `;

            this.db.serialize(() => {
                this.db.run(createUsersTable, (err) => {
                    if (err) {
                        console.error('❌ users 테이블 생성 실패:', err);
                        reject(err);
                        return;
                    }
                    console.log('✅ users 테이블 생성 완료');
                });

                this.db.run(createSessionsTable, (err) => {
                    if (err) {
                        console.error('❌ sessions 테이블 생성 실패:', err);
                        reject(err);
                        return;
                    }
                    console.log('✅ sessions 테이블 생성 완료');
                });

                this.db.run(createIndexes, (err) => {
                    if (err) {
                        console.error('❌ 인덱스 생성 실패:', err);
                        reject(err);
                        return;
                    }
                    console.log('✅ 인덱스 생성 완료');
                    resolve();
                });
            });
        });
    }

    // 사용자 생성
    async createUser(userData) {
        return new Promise((resolve, reject) => {
            const {
                username,
                email,
                password_hash,
                full_name,
                phone,
                role = 'user',
                additional_info = {}
            } = userData;

            const sql = `
                INSERT INTO users (username, email, password_hash, full_name, phone, role, additional_info)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            `;

            this.db.run(sql, [
                username,
                email,
                password_hash,
                full_name,
                phone,
                role,
                JSON.stringify(additional_info)
            ], function(err) {
                if (err) {
                    console.error('❌ 사용자 생성 실패:', err);
                    reject(err);
                } else {
                    console.log('✅ 사용자 생성 성공:', username);
                    resolve({
                        id: this.lastID,
                        username,
                        email,
                        full_name,
                        phone,
                        role,
                        additional_info
                    });
                }
            });
        });
    }

    // 사용자명으로 사용자 조회
    async getUserByUsername(username) {
        return new Promise((resolve, reject) => {
            const sql = 'SELECT * FROM users WHERE username = ?';
            this.db.get(sql, [username], (err, row) => {
                if (err) {
                    console.error('❌ 사용자 조회 실패:', err);
                    reject(err);
                } else {
                    if (row && row.additional_info) {
                        try {
                            row.additional_info = JSON.parse(row.additional_info);
                        } catch (e) {
                            console.warn('⚠️ additional_info 파싱 실패:', e);
                        }
                    }
                    resolve(row);
                }
            });
        });
    }

    // 이메일로 사용자 조회
    async getUserByEmail(email) {
        return new Promise((resolve, reject) => {
            const sql = 'SELECT * FROM users WHERE email = ?';
            this.db.get(sql, [email], (err, row) => {
                if (err) {
                    console.error('❌ 사용자 조회 실패:', err);
                    reject(err);
                } else {
                    if (row && row.additional_info) {
                        try {
                            row.additional_info = JSON.parse(row.additional_info);
                        } catch (e) {
                            console.warn('⚠️ additional_info 파싱 실패:', e);
                        }
                    }
                    resolve(row);
                }
            });
        });
    }

    // 사용자 ID로 조회
    async getUserById(id) {
        return new Promise((resolve, reject) => {
            const sql = 'SELECT * FROM users WHERE id = ?';
            this.db.get(sql, [id], (err, row) => {
                if (err) {
                    console.error('❌ 사용자 조회 실패:', err);
                    reject(err);
                } else {
                    if (row && row.additional_info) {
                        try {
                            row.additional_info = JSON.parse(row.additional_info);
                        } catch (e) {
                            console.warn('⚠️ additional_info 파싱 실패:', e);
                        }
                    }
                    resolve(row);
                }
            });
        });
    }

    // 마지막 로그인 시간 업데이트
    async updateUserLastLogin(userId) {
        return new Promise((resolve, reject) => {
            const sql = 'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?';
            this.db.run(sql, [userId], (err) => {
                if (err) {
                    console.error('❌ 로그인 시간 업데이트 실패:', err);
                    reject(err);
                } else {
                    resolve();
                }
            });
        });
    }

    // 세션 생성
    async createSession(sessionId, userId, expiresAt) {
        return new Promise((resolve, reject) => {
            const sql = `
                INSERT INTO sessions (session_id, user_id, expires_at)
                VALUES (?, ?, ?)
            `;
            this.db.run(sql, [sessionId, userId, expiresAt], (err) => {
                if (err) {
                    console.error('❌ 세션 생성 실패:', err);
                    reject(err);
                } else {
                    console.log('✅ 세션 생성 성공:', sessionId);
                    resolve();
                }
            });
        });
    }

    // 세션 조회
    async getSession(sessionId) {
        return new Promise((resolve, reject) => {
            const sql = `
                SELECT s.*, u.username, u.email, u.full_name, u.role, u.additional_info
                FROM sessions s
                JOIN users u ON s.user_id = u.id
                WHERE s.session_id = ? AND s.expires_at > CURRENT_TIMESTAMP
            `;
            this.db.get(sql, [sessionId], (err, row) => {
                if (err) {
                    console.error('❌ 세션 조회 실패:', err);
                    reject(err);
                } else {
                    if (row && row.additional_info) {
                        try {
                            row.additional_info = JSON.parse(row.additional_info);
                        } catch (e) {
                            console.warn('⚠️ additional_info 파싱 실패:', e);
                        }
                    }
                    resolve(row);
                }
            });
        });
    }

    // 세션 삭제
    async deleteSession(sessionId) {
        return new Promise((resolve, reject) => {
            const sql = 'DELETE FROM sessions WHERE session_id = ?';
            this.db.run(sql, [sessionId], (err) => {
                if (err) {
                    console.error('❌ 세션 삭제 실패:', err);
                    reject(err);
                } else {
                    console.log('✅ 세션 삭제 성공:', sessionId);
                    resolve();
                }
            });
        });
    }

    // 만료된 세션 정리
    async cleanupExpiredSessions() {
        return new Promise((resolve, reject) => {
            const sql = 'DELETE FROM sessions WHERE expires_at <= CURRENT_TIMESTAMP';
            this.db.run(sql, (err) => {
                if (err) {
                    console.error('❌ 만료된 세션 정리 실패:', err);
                    reject(err);
                } else {
                    console.log('✅ 만료된 세션 정리 완료');
                    resolve();
                }
            });
        });
    }

    // 데이터베이스 연결 종료
    close() {
        if (this.db) {
            this.db.close((err) => {
                if (err) {
                    console.error('❌ 데이터베이스 연결 종료 실패:', err);
                } else {
                    console.log('✅ 데이터베이스 연결 종료');
                }
            });
        }
    }
}

module.exports = SQLiteDatabaseService;
