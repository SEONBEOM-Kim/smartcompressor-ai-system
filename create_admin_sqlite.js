/**
 * SQLite 관리자 계정 생성 스크립트
 * 배포 환경에서 사용할 관리자 계정을 생성합니다.
 */

const SQLiteDatabaseService = require('./services/sqlite_database_service');
const bcrypt = require('bcryptjs');

async function createAdminAccount() {
    const db = new SQLiteDatabaseService();
    
    try {
        // 데이터베이스 초기화 완료 대기
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // 관리자 계정 정보
        const adminData = {
            username: 'admin',
            email: 'admin@signalcraft.kr',
            password: 'admin123!@#',
            full_name: '시스템 관리자',
            phone: '010-0000-0000',
            role: 'admin',
            additional_info: {
                position: '시스템 관리자',
                company: '시그널크래프트',
                industry: 'IT',
                company_size: '1-10명',
                preferences: {
                    email_alerts: true,
                    email_newsletter: true,
                    sms_alerts: false,
                    kakao_alerts: false,
                    marketing_agree: false
                }
            }
        };

        // 기존 관리자 계정 확인
        const existingAdmin = await db.getUserByUsername('admin');
        if (existingAdmin) {
            console.log('⚠️ 관리자 계정이 이미 존재합니다.');
            console.log('📧 이메일:', existingAdmin.email);
            console.log('👤 사용자명:', existingAdmin.username);
            console.log('🔑 비밀번호: admin123!@#');
            return;
        }

        // 비밀번호 해시화
        const saltRounds = 10;
        const password_hash = await bcrypt.hash(adminData.password, saltRounds);

        // 관리자 계정 생성
        const adminUser = await db.createUser({
            ...adminData,
            password_hash
        });

        console.log('✅ 관리자 계정 생성 완료!');
        console.log('👤 사용자명:', adminUser.username);
        console.log('📧 이메일:', adminUser.email);
        console.log('🔑 비밀번호:', adminData.password);
        console.log('🔐 역할:', adminUser.role);
        console.log('');
        console.log('🌐 로그인 URL: http://signalcraft.kr:3000');
        console.log('👨‍💼 관리자 대시보드: http://signalcraft.kr:3000/admin');

    } catch (error) {
        console.error('❌ 관리자 계정 생성 실패:', error);
    } finally {
        db.close();
    }
}

// 스크립트 실행
createAdminAccount();
