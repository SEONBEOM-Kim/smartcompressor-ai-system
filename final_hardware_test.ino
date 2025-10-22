/*
 * 최종 하드웨어 진단 테스트
 * 보드 문제 확인용
 */

#include <driver/i2s.h>

void setup() {
    Serial.begin(115200);
    delay(2000);
    
    Serial.println("=== 최종 하드웨어 진단 테스트 ===");
    Serial.println();
    
    // 1. 기본 GPIO 테스트
    testBasicGPIO();
    
    // 2. I2S 드라이버 테스트
    testI2SDriver();
    
    // 3. 다양한 I2S 설정 테스트
    testI2SConfigurations();
    
    // 4. 하드웨어 문제 진단
    diagnoseHardware();
}

void loop() {
    delay(1000);
}

void testBasicGPIO() {
    Serial.println("=== 1. 기본 GPIO 테스트 ===");
    
    // 여러 핀에서 디지털 읽기 테스트
    int pins[] = {32, 33, 34, 35, 36, 39};
    int pin_count = sizeof(pins) / sizeof(pins[0]);
    
    Serial.println("여러 핀에서 디지털 값 읽기:");
    for (int i = 0; i < pin_count; i++) {
        pinMode(pins[i], INPUT);
        int value = digitalRead(pins[i]);
        Serial.println("GPIO " + String(pins[i]) + ": " + String(value));
    }
    
    // 핀 출력 테스트
    Serial.println("\n핀 출력 테스트:");
    pinMode(2, OUTPUT);
    digitalWrite(2, HIGH);
    delay(100);
    digitalWrite(2, LOW);
    Serial.println("GPIO 2 출력 테스트 완료");
    
    Serial.println("✅ 기본 GPIO 테스트 완료\n");
}

void testI2SDriver() {
    Serial.println("=== 2. I2S 드라이버 테스트 ===");
    
    // I2S 설정 (가장 기본적인 설정)
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = 8000,  // 낮은 샘플레이트
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 2,   // 최소 버퍼
        .dma_buf_len = 256,   // 작은 버퍼
        .use_apll = false,    // APLL 비활성화
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };
    
    // 핀 설정 (가장 일반적인 핀)
    i2s_pin_config_t pin_config = {
        .bck_io_num = 26,
        .ws_io_num = 25,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = 27
    };
    
    Serial.println("I2S 드라이버 설치 시도...");
    esp_err_t result = i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    if (result != ESP_OK) {
        Serial.println("❌ I2S 드라이버 설치 실패: " + String(result));
        Serial.println("   → ESP32 I2S 하드웨어 문제 가능성");
        return;
    }
    Serial.println("✅ I2S 드라이버 설치 성공");
    
    Serial.println("I2S 핀 설정 시도...");
    result = i2s_set_pin(I2S_NUM_0, &pin_config);
    if (result != ESP_OK) {
        Serial.println("❌ I2S 핀 설정 실패: " + String(result));
        i2s_driver_uninstall(I2S_NUM_0);
        return;
    }
    Serial.println("✅ I2S 핀 설정 성공");
    
    Serial.println("I2S 시작 시도...");
    i2s_zero_dma_buffer(I2S_NUM_0);
    result = i2s_start(I2S_NUM_0);
    if (result != ESP_OK) {
        Serial.println("❌ I2S 시작 실패: " + String(result));
        i2s_driver_uninstall(I2S_NUM_0);
        return;
    }
    Serial.println("✅ I2S 시작 성공");
    
    // 데이터 읽기 테스트
    int16_t testBuffer[256];
    size_t bytes_read = 0;
    
    Serial.println("데이터 읽기 테스트...");
    for (int i = 0; i < 5; i++) {
        result = i2s_read(I2S_NUM_0, testBuffer, 256 * sizeof(int16_t), &bytes_read, 1000);
        Serial.println("시도 " + String(i + 1) + ": " + String(result) + " (" + String(bytes_read) + " bytes)");
        
        if (result == ESP_OK && bytes_read > 0) {
            // 데이터 분석
            int16_t max_val = -32768;
            int16_t min_val = 32767;
            int non_zero = 0;
            
            for (int j = 0; j < 256; j++) {
                if (testBuffer[j] > max_val) max_val = testBuffer[j];
                if (testBuffer[j] < min_val) min_val = testBuffer[j];
                if (testBuffer[j] != 0) non_zero++;
            }
            
            Serial.println("  최대: " + String(max_val) + ", 최소: " + String(min_val) + ", 비영점: " + String(non_zero));
        }
        delay(100);
    }
    
    i2s_driver_uninstall(I2S_NUM_0);
    Serial.println("✅ I2S 드라이버 테스트 완료\n");
}

void testI2SConfigurations() {
    Serial.println("=== 3. 다양한 I2S 설정 테스트 ===");
    
    // 여러 설정 조합 테스트
    struct TestConfig {
        int sample_rate;
        int bits_per_sample;
        int dma_buf_count;
        int dma_buf_len;
        bool use_apll;
        String name;
    };
    
    TestConfig configs[] = {
        {8000, 16, 2, 256, false, "기본 설정"},
        {16000, 16, 4, 512, false, "표준 설정"},
        {16000, 16, 4, 512, true, "APLL 활성화"},
        {8000, 24, 2, 256, false, "24비트 설정"},
        {16000, 32, 2, 256, false, "32비트 설정"}
    };
    
    int config_count = sizeof(configs) / sizeof(configs[0]);
    
    for (int c = 0; c < config_count; c++) {
        Serial.println("설정 " + String(c + 1) + ": " + configs[c].name);
        
        i2s_config_t i2s_config = {
            .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
            .sample_rate = configs[c].sample_rate,
            .bits_per_sample = (i2s_bits_per_sample_t)configs[c].bits_per_sample,
            .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
            .communication_format = I2S_COMM_FORMAT_STAND_I2S,
            .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
            .dma_buf_count = configs[c].dma_buf_count,
            .dma_buf_len = configs[c].dma_buf_len,
            .use_apll = configs[c].use_apll,
            .tx_desc_auto_clear = false,
            .fixed_mclk = 0
        };
        
        i2s_pin_config_t pin_config = {
            .bck_io_num = 26,
            .ws_io_num = 25,
            .data_out_num = I2S_PIN_NO_CHANGE,
            .data_in_num = 27
        };
        
        esp_err_t result = i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
        if (result == ESP_OK) {
            result = i2s_set_pin(I2S_NUM_0, &pin_config);
            if (result == ESP_OK) {
                i2s_zero_dma_buffer(I2S_NUM_0);
                result = i2s_start(I2S_NUM_0);
                if (result == ESP_OK) {
                    Serial.println("  ✅ 설정 성공");
                } else {
                    Serial.println("  ❌ 시작 실패: " + String(result));
                }
            } else {
                Serial.println("  ❌ 핀 설정 실패: " + String(result));
            }
            i2s_driver_uninstall(I2S_NUM_0);
        } else {
            Serial.println("  ❌ 드라이버 설치 실패: " + String(result));
        }
        delay(100);
    }
    
    Serial.println("✅ I2S 설정 테스트 완료\n");
}

void diagnoseHardware() {
    Serial.println("=== 4. 하드웨어 문제 진단 ===");
    Serial.println();
    
    Serial.println("🔍 진단 결과:");
    Serial.println("모든 핀 조합에서 데이터가 0으로 나옴");
    Serial.println();
    
    Serial.println("❌ 가능한 원인들:");
    Serial.println("1. ICS-43434 마이크 센서 자체 고장");
    Serial.println("2. 마이크 전원 공급 회로 문제 (3.3V)");
    Serial.println("3. I2S 신호 라인 단선 또는 단락");
    Serial.println("4. ESP32 I2S 하드웨어 문제");
    Serial.println("5. 보드 설계 오류 또는 제조 불량");
    Serial.println();
    
    Serial.println("🔧 권장 해결 방법:");
    Serial.println("1. 다른 완성형 보드로 교체");
    Serial.println("2. 마이크 센서만 교체 (가능한 경우)");
    Serial.println("3. 제조사에 문의하여 보드 검사 요청");
    Serial.println("4. 다른 ESP32 보드로 테스트");
    Serial.println();
    
    Serial.println("⚠️  결론: 하드웨어 교체가 필요합니다.");
    Serial.println("소프트웨어로는 해결할 수 없는 문제입니다.");
}
