/**
 * 라벨링 데이터베이스 (SQLite)
 * 실제 라벨링 데이터를 영구 저장
 */

const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

class LabelingDatabase {
    constructor() {
        // 데이터 디렉토리 생성
        const dataDir = path.join(__dirname, '..', 'data');
        if (!fs.existsSync(dataDir)) {
            fs.mkdirSync(dataDir, { recursive: true });
        }
        
        this.dbPath = path.join(dataDir, 'labeling.db');
        this.db = new sqlite3.Database(this.dbPath);
        this.init();
    }

    init() {
        // 라벨링 테이블 생성
        this.db.run(`
            CREATE TABLE IF NOT EXISTS labels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_size INTEGER,
                file_type TEXT,
                label TEXT NOT NULL,
                confidence INTEGER NOT NULL,
                notes TEXT,
                labeler_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // 전문가 테이블 생성
        this.db.run(`
            CREATE TABLE IF NOT EXISTS experts (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        `);

        // 라벨링 통계 테이블 생성
        this.db.run(`
            CREATE TABLE IF NOT EXISTS labeling_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                total_labeled INTEGER DEFAULT 0,
                normal_count INTEGER DEFAULT 0,
                warning_count INTEGER DEFAULT 0,
                critical_count INTEGER DEFAULT 0,
                unknown_count INTEGER DEFAULT 0,
                avg_confidence REAL DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date)
            )
        `);

        console.log('📊 라벨링 데이터베이스 초기화 완료');
    }

    // 라벨 저장
    saveLabel(labelData) {
        return new Promise((resolve, reject) => {
            const sql = `
                INSERT INTO labels (file_name, file_size, file_type, label, confidence, notes, labeler_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            `;
            
            this.db.run(sql, [
                labelData.file_name,
                labelData.file_size,
                labelData.file_type,
                labelData.label,
                labelData.confidence,
                labelData.notes,
                labelData.labeler_id
            ], function(err) {
                if (err) {
                    reject(err);
                } else {
                    resolve({
                        id: this.lastID,
                        ...labelData,
                        created_at: new Date().toISOString()
                    });
                }
            });
        });
    }

    // 라벨링 통계 조회
    getStats() {
        return new Promise((resolve, reject) => {
            const stats = {};
            
            // 총 라벨링 수
            this.db.get('SELECT COUNT(*) as total FROM labels', (err, row) => {
                if (err) {
                    reject(err);
                    return;
                }
                stats.total_labeled = row.total;
                
                // 오늘 라벨링 수
                this.db.get(`
                    SELECT COUNT(*) as today FROM labels 
                    WHERE DATE(timestamp) = DATE('now')
                `, (err, row) => {
                    if (err) {
                        reject(err);
                        return;
                    }
                    stats.today_labeled = row.today;
                    
                    // 라벨 분포
                    this.db.all(`
                        SELECT label, COUNT(*) as count 
                        FROM labels 
                        GROUP BY label
                    `, (err, rows) => {
                        if (err) {
                            reject(err);
                            return;
                        }
                        
                        stats.label_distribution = {
                            normal: 0,
                            warning: 0,
                            critical: 0,
                            unknown: 0
                        };
                        
                        rows.forEach(row => {
                            stats.label_distribution[row.label] = row.count;
                        });
                        
                        // 평균 신뢰도
                        this.db.get(`
                            SELECT AVG(confidence) as avg_confidence 
                            FROM labels
                        `, (err, row) => {
                            if (err) {
                                reject(err);
                                return;
                            }
                            
                            stats.accuracy = Math.round((row.avg_confidence || 0) * 10) / 10;
                            
                            // 최근 활동
                            this.db.all(`
                                SELECT file_name, label, confidence, timestamp
                                FROM labels 
                                ORDER BY timestamp DESC 
                                LIMIT 5
                            `, (err, rows) => {
                                if (err) {
                                    reject(err);
                                    return;
                                }
                                
                                stats.recent_activity = rows.map(row => ({
                                    file: row.file_name,
                                    label: row.label,
                                    confidence: row.confidence,
                                    timestamp: row.timestamp
                                }));
                                
                                resolve(stats);
                            });
                        });
                    });
                });
            });
        });
    }

    // 라벨링 이력 조회
    getHistory(options = {}) {
        return new Promise((resolve, reject) => {
            const { page = 1, limit = 20, label } = options;
            const offset = (page - 1) * limit;
            
            let sql = 'SELECT * FROM labels';
            let params = [];
            
            if (label) {
                sql += ' WHERE label = ?';
                params.push(label);
            }
            
            sql += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?';
            params.push(limit, offset);
            
            this.db.all(sql, params, (err, rows) => {
                if (err) {
                    reject(err);
                    return;
                }
                
                // 총 개수 조회
                let countSql = 'SELECT COUNT(*) as total FROM labels';
                let countParams = [];
                
                if (label) {
                    countSql += ' WHERE label = ?';
                    countParams.push(label);
                }
                
                this.db.get(countSql, countParams, (err, row) => {
                    if (err) {
                        reject(err);
                        return;
                    }
                    
                    resolve({
                        history: rows,
                        pagination: {
                            page: page,
                            limit: limit,
                            total: row.total,
                            total_pages: Math.ceil(row.total / limit)
                        }
                    });
                });
            });
        });
    }

    // 전문가 등록
    registerExpert(expertData) {
        return new Promise((resolve, reject) => {
            const sql = `
                INSERT OR REPLACE INTO experts (id, name, email, last_active)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            `;
            
            this.db.run(sql, [
                expertData.id,
                expertData.name,
                expertData.email
            ], function(err) {
                if (err) {
                    reject(err);
                } else {
                    resolve(expertData);
                }
            });
        });
    }

    // 전문가 목록 조회
    getExperts() {
        return new Promise((resolve, reject) => {
            this.db.all(`
                SELECT e.*, 
                       COUNT(l.id) as total_labeled,
                       AVG(l.confidence) as avg_confidence
                FROM experts e
                LEFT JOIN labels l ON e.id = l.labeler_id
                GROUP BY e.id
                ORDER BY total_labeled DESC
            `, (err, rows) => {
                if (err) {
                    reject(err);
                } else {
                    resolve(rows.map(row => ({
                        id: row.id,
                        name: row.name,
                        email: row.email,
                        total_labeled: row.total_labeled || 0,
                        avg_confidence: Math.round((row.avg_confidence || 0) * 10) / 10,
                        last_active: row.last_active
                    })));
                }
            });
        });
    }

    // 데이터베이스 닫기
    close() {
        this.db.close();
    }
}

module.exports = LabelingDatabase;
