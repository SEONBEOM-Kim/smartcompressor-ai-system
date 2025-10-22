const express = require('express');
const router = express.Router();

// 기상 데이터 캐싱
let weatherCache = null;
let lastWeatherUpdate = 0;
const WEATHER_UPDATE_INTERVAL = 30 * 60 * 1000; // 30분마다 업데이트

// OpenWeatherMap API 키 (환경변수에서 가져오기)
const OPENWEATHER_API_KEY = process.env.OPENWEATHER_API_KEY || 'YOUR_OPENWEATHER_API_KEY';

// 현재 기상 데이터 조회
router.get('/current', async (req, res) => {
    try {
        const now = Date.now();
        
        // 캐시된 데이터가 있고 30분 이내라면 캐시 사용
        if (weatherCache && (now - lastWeatherUpdate) < WEATHER_UPDATE_INTERVAL) {
            console.log('🌡️ 기상 데이터 캐시 사용');
            return res.json({
                success: true,
                ...weatherCache,
                cached: true
            });
        }

        // OpenWeatherMap API 호출
        const response = await fetch(`https://api.openweathermap.org/data/2.5/weather?lat=37.5665&lon=126.9780&appid=${OPENWEATHER_API_KEY}&units=metric`);
        
        if (!response.ok) {
            throw new Error(`OpenWeatherMap API 오류: ${response.status}`);
        }

        const data = await response.json();
        
        // 캐시 업데이트
        weatherCache = {
            temperature: data.main.temp,
            humidity: data.main.humidity,
            location: data.name,
            description: data.weather[0].description,
            timestamp: now
        };
        lastWeatherUpdate = now;

        console.log('🌡️ 기상 데이터 업데이트:', weatherCache);

        res.json({
            success: true,
            ...weatherCache,
            cached: false
        });

    } catch (error) {
        console.error('기상 데이터 가져오기 실패:', error);
        
        // 캐시된 데이터가 있다면 그것을 반환
        if (weatherCache) {
            console.log('🌡️ 캐시된 기상 데이터 사용 (API 오류)');
            return res.json({
                success: true,
                ...weatherCache,
                cached: true,
                warning: 'API 오류로 인해 캐시된 데이터 사용'
            });
        }

        res.status(500).json({
            success: false,
            message: '기상 데이터를 가져올 수 없습니다',
            error: error.message
        });
    }
});

// 기상 데이터 통계 (선택사항)
router.get('/stats', (req, res) => {
    res.json({
        success: true,
        lastUpdate: lastWeatherUpdate,
        updateInterval: WEATHER_UPDATE_INTERVAL,
        cacheAge: Date.now() - lastWeatherUpdate,
        hasCache: !!weatherCache
    });
});

module.exports = router;
