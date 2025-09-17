const axios = require('axios');
const kakaoConfig = require('../config/kakao');

class KakaoService {
    // 카카오 로그인 URL 생성
    getLoginUrl() {
        const params = new URLSearchParams({
            client_id: kakaoConfig.restApiKey,
            redirect_uri: kakaoConfig.redirectUri,
            response_type: 'code'
        });

        return `https://kauth.kakao.com/oauth/authorize?${params.toString()}`;
    }

    // 카카오 액세스 토큰으로 사용자 정보 조회
    async getUserInfo(accessToken) {
        try {
            const response = await axios.get(kakaoConfig.apiEndpoints.userInfo, {
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
                }
            });

            const userInfo = response.data;
            
            return {
                success: true,
                user: {
                    id: userInfo.id,
                    email: userInfo.kakao_account?.email || `kakao_${userInfo.id}@kakao.com`,
                    name: userInfo.kakao_account?.profile?.nickname || `카카오사용자${userInfo.id}`,
                    profile_image: userInfo.kakao_account?.profile?.profile_image_url,
                    thumbnail_image: userInfo.kakao_account?.profile?.thumbnail_image_url,
                    provider: 'kakao',
                    provider_id: userInfo.id.toString()
                }
            };
        } catch (error) {
            console.error('카카오 사용자 정보 조회 오류:', error.response?.data || error.message);
            return {
                success: false,
                message: '카카오 사용자 정보를 가져올 수 없습니다.'
            };
        }
    }

    // 카카오 로그인 처리
    async login(accessToken) {
        try {
            // 카카오에서 사용자 정보 조회
            const userInfoResult = await this.getUserInfo(accessToken);
            
            if (!userInfoResult.success) {
                return userInfoResult;
            }

            const kakaoUser = userInfoResult.user;
            
            // 간단한 세션 ID 생성 (실제로는 데이터베이스에 저장)
            const sessionId = `kakao_${kakaoUser.id}_${Date.now()}`;

            return {
                success: true,
                message: '카카오 로그인 성공',
                sessionId: sessionId,
                user: {
                    id: kakaoUser.id,
                    email: kakaoUser.email,
                    name: kakaoUser.name,
                    provider: 'kakao',
                    profile_image: kakaoUser.profile_image,
                    thumbnail_image: kakaoUser.thumbnail_image
                }
            };

        } catch (error) {
            console.error('카카오 로그인 오류:', error);
            return {
                success: false,
                message: '카카오 로그인 중 오류가 발생했습니다.'
            };
        }
    }

    // 카카오 인증 코드로 액세스 토큰 발급
    async getAccessToken(code) {
        try {
            const response = await axios.post(kakaoConfig.apiEndpoints.token, {
                grant_type: 'authorization_code',
                client_id: kakaoConfig.restApiKey,
                client_secret: kakaoConfig.clientSecret,
                redirect_uri: kakaoConfig.redirectUri,
                code: code
            }, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
                }
            });

            return {
                success: true,
                access_token: response.data.access_token,
                refresh_token: response.data.refresh_token,
                expires_in: response.data.expires_in
            };
        } catch (error) {
            console.error('카카오 액세스 토큰 발급 오류:', error.response?.data || error.message);
            return {
                success: false,
                message: '카카오 액세스 토큰을 발급받을 수 없습니다.'
            };
        }
    }

    // 카카오 로그아웃
    async logout(accessToken) {
        try {
            if (accessToken) {
                await axios.post(kakaoConfig.apiEndpoints.logout, {}, {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`,
                        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
                    }
                });
            }
            
            return {
                success: true,
                message: '카카오 로그아웃 성공'
            };
        } catch (error) {
            console.error('카카오 로그아웃 오류:', error.response?.data || error.message);
            return {
                success: true,
                message: '서버 세션은 삭제되었습니다.'
            };
        }
    }
}

module.exports = new KakaoService();