/**
 * 자동 업로드 스크립트
 * 로컬 데이터를 클라우드 데이터베이스로 자동 동기화
 */

const DatabaseService = require('../services/database_service');
const fs = require('fs');
const path = require('path');
const cron = require('node-cron');

class AutoUploadService {
    constructor() {
        this.localDB = new DatabaseService();
        this.cloudDB = new DatabaseService(); // 클라우드 설정으로 초기화
        this.isRunning = false;
    }

    // 자동 업로드 시작
    start() {
        console.log('🚀 자동 업로드 서비스 시작');
        
        // 5분마다 실행
        cron.schedule('*/5 * * * *', () => {
            if (!this.isRunning) {
                this.uploadPendingData();
            }
        });

        // 1시간마다 전체 동기화
        cron.schedule('0 * * * *', () => {
            if (!this.isRunning) {
                this.fullSync();
            }
        });
    }

    // 대기 중인 데이터 업로드
    async uploadPendingData() {
        this.isRunning = true;
        
        try {
            console.log('📤 대기 중인 데이터 업로드 시작...');
            
            // 로컬에서 업로드되지 않은 데이터 조회
            const pendingData = await this.getPendingData();
            
            if (pendingData.length === 0) {
                console.log('✅ 업로드할 데이터가 없습니다.');
                return;
            }

            console.log(`📊 ${pendingData.length}개의 레코드를 업로드합니다.`);

            // 클라우드로 업로드
            for (const data of pendingData) {
                try {
                    await this.cloudDB.saveLabel(data);
                    await this.markAsUploaded(data.id);
                    console.log(`✅ 업로드 완료: ${data.file_name}`);
                } catch (error) {
                    console.error(`❌ 업로드 실패: ${data.file_name}`, error.message);
                }
            }

            console.log('🎉 업로드 완료!');
            
        } catch (error) {
            console.error('❌ 업로드 중 오류:', error);
        } finally {
            this.isRunning = false;
        }
    }

    // 전체 동기화
    async fullSync() {
        this.isRunning = true;
        
        try {
            console.log('🔄 전체 동기화 시작...');
            
            // 로컬 데이터 전체 조회
            const localData = await this.localDB.getHistory({ limit: 1000 });
            
            // 클라우드 데이터와 비교하여 동기화
            for (const data of localData.history) {
                try {
                    const exists = await this.checkIfExistsInCloud(data);
                    if (!exists) {
                        await this.cloudDB.saveLabel(data);
                        console.log(`✅ 동기화 완료: ${data.file_name}`);
                    }
                } catch (error) {
                    console.error(`❌ 동기화 실패: ${data.file_name}`, error.message);
                }
            }

            console.log('🎉 전체 동기화 완료!');
            
        } catch (error) {
            console.error('❌ 동기화 중 오류:', error);
        } finally {
            this.isRunning = false;
        }
    }

    // 대기 중인 데이터 조회
    async getPendingData() {
        // 실제로는 uploaded_to_cloud 플래그로 확인
        // 여기서는 시뮬레이션
        return [];
    }

    // 클라우드에 존재하는지 확인
    async checkIfExistsInCloud(data) {
        // 실제로는 클라우드 DB에서 확인
        return false;
    }

    // 업로드 완료 표시
    async markAsUploaded(id) {
        // 실제로는 로컬 DB에 업로드 완료 플래그 설정
        console.log(`📝 업로드 완료 표시: ${id}`);
    }

    // 수동 업로드
    async manualUpload() {
        console.log('🔧 수동 업로드 시작...');
        await this.uploadPendingData();
    }

    // 서비스 중지
    stop() {
        console.log('⏹️ 자동 업로드 서비스 중지');
        cron.destroy();
    }
}

// CLI 실행
if (require.main === module) {
    const autoUpload = new AutoUploadService();
    
    const command = process.argv[2];
    
    switch (command) {
        case 'start':
            autoUpload.start();
            break;
        case 'upload':
            autoUpload.manualUpload().then(() => process.exit(0));
            break;
        case 'sync':
            autoUpload.fullSync().then(() => process.exit(0));
            break;
        default:
            console.log(`
사용법:
  node scripts/auto_upload.js start   # 자동 업로드 서비스 시작
  node scripts/auto_upload.js upload  # 수동 업로드
  node scripts/auto_upload.js sync    # 전체 동기화
            `);
    }
}

module.exports = AutoUploadService;
