const fs = require('fs');
const path = require('path');

class ESP32DataManager {
    constructor() {
        this.dataDir = path.join(__dirname, '../../data/esp32_features');
        this.ensureDataDir();
    }

    ensureDataDir() {
        if (!fs.existsSync(this.dataDir)) {
            fs.mkdirSync(this.dataDir, { recursive: true });
        }
    }

    // 데이터 저장 (일별 파일로 분할)
    saveData(data) {
        const today = new Date().toISOString().split('T')[0];
        const filename = `esp32_data_${today}.json`;
        const filepath = path.join(this.dataDir, filename);

        let existingData = [];
        if (fs.existsSync(filepath)) {
            try {
                const content = fs.readFileSync(filepath, 'utf8');
                existingData = JSON.parse(content);
            } catch (error) {
                console.error('기존 데이터 읽기 오류:', error);
            }
        }

        // 새 데이터 추가
        existingData.push({
            ...data,
            server_timestamp: Date.now(),
            received_at: new Date().toISOString()
        });

        // 파일 저장
        try {
            fs.writeFileSync(filepath, JSON.stringify(existingData, null, 2));
            console.log(`데이터 저장 완료: ${filepath}`);
            return true;
        } catch (error) {
            console.error('데이터 저장 오류:', error);
            return false;
        }
    }

    // 데이터 조회 (최근 데이터)
    getRecentData(options = {}) {
        const {
            limit = 50,
            sensorId = null,
            hours = 24
        } = options;

        const files = fs.readdirSync(this.dataDir)
            .filter(file => file.endsWith('.json'))
            .sort((a, b) => {
                const statA = fs.statSync(path.join(this.dataDir, a));
                const statB = fs.statSync(path.join(this.dataDir, b));
                return statB.mtime - statA.mtime;
            });

        let allData = [];
        const cutoffTime = Date.now() - (hours * 60 * 60 * 1000);

        // 최근 파일들에서 데이터 읽기
        for (let i = 0; i < Math.min(files.length, 7); i++) { // 최근 7일
            try {
                const filePath = path.join(this.dataDir, files[i]);
                const fileContent = fs.readFileSync(filePath, 'utf8');
                const data = JSON.parse(fileContent);

                if (Array.isArray(data)) {
                    allData = allData.concat(data);
                } else {
                    allData.push(data);
                }
            } catch (error) {
                console.error('파일 읽기 오류:', error);
            }
        }

        // 시간 필터링
        allData = allData.filter(item => item.server_timestamp > cutoffTime);

        // 센서 ID 필터링
        if (sensorId) {
            allData = allData.filter(item => item.device_id === sensorId);
        }

        // 시간순 정렬
        allData.sort((a, b) => b.server_timestamp - a.server_timestamp);

        // 제한된 개수 반환
        return allData.slice(0, Math.min(limit, 200));
    }

    // 데이터 통계
    getDataStats() {
        const files = fs.readdirSync(this.dataDir)
            .filter(file => file.endsWith('.json'));

        let totalRecords = 0;
        let totalSize = 0;
        const sensorIds = new Set();

        files.forEach(file => {
            try {
                const filePath = path.join(this.dataDir, file);
                const stats = fs.statSync(filePath);
                totalSize += stats.size;

                const content = fs.readFileSync(filePath, 'utf8');
                const data = JSON.parse(content);
                
                if (Array.isArray(data)) {
                    totalRecords += data.length;
                    data.forEach(item => {
                        if (item.device_id) {
                            sensorIds.add(item.device_id);
                        }
                    });
                }
            } catch (error) {
                console.error('통계 계산 오류:', error);
            }
        });

        return {
            totalFiles: files.length,
            totalRecords,
            totalSizeMB: (totalSize / 1024 / 1024).toFixed(2),
            uniqueSensors: sensorIds.size,
            sensors: Array.from(sensorIds)
        };
    }

    // 오래된 데이터 정리 (30일 이상)
    cleanupOldData() {
        const files = fs.readdirSync(this.dataDir)
            .filter(file => file.endsWith('.json'));

        const thirtyDaysAgo = Date.now() - (30 * 24 * 60 * 60 * 1000);
        let deletedFiles = 0;

        files.forEach(file => {
            try {
                const filePath = path.join(this.dataDir, file);
                const stats = fs.statSync(filePath);
                
                if (stats.mtime.getTime() < thirtyDaysAgo) {
                    fs.unlinkSync(filePath);
                    deletedFiles++;
                    console.log(`오래된 파일 삭제: ${file}`);
                }
            } catch (error) {
                console.error('파일 삭제 오류:', error);
            }
        });

        return deletedFiles;
    }
}

module.exports = ESP32DataManager;
