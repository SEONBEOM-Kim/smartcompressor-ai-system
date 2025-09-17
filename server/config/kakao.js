// 카카오 로그인 설정
const kakaoConfig = {
    // 카카오 앱 키들
    nativeAppKey: process.env.KAKAO_NATIVE_APP_KEY || '6a3568bea9b962282d0bfb87411f1fc8',
    restApiKey: process.env.KAKAO_REST_API_KEY || 'cac4914ad015391f526e9f58ac815111',
    javascriptKey: process.env.KAKAO_JAVASCRIPT_KEY || 'fc290e3883b18dc31a3ce7790c30cb9c',
    adminKey: process.env.KAKAO_ADMIN_KEY || 'c2ccf68a6300bf4aff2f881936662ecb',
    clientSecret: process.env.KAKAO_CLIENT_SECRET || 'W6DhnArUAvNZDYMw9cH11r3IQIR3vAXk',
    
    // 리다이렉트 URI (카카오 개발자 콘솔에 등록된 URI 사용)
    redirectUri: process.env.KAKAO_REDIRECT_URI || 'https://signalcraft.kr/auth/kakao/callback',
    
    // 카카오 API 엔드포인트
    apiEndpoints: {
        token: 'https://kauth.kakao.com/oauth/token',
        userInfo: 'https://kapi.kakao.com/v2/user/me',
        logout: 'https://kapi.kakao.com/v1/user/logout'
    }
};

module.exports = kakaoConfig;
