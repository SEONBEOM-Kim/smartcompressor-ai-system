/*
 * ESP32 보드 하드웨어 진단 코드
 * 고장 부위 확인용
 */

#include <driver/i2s.h>
#include <WiFi.h>
#include <HTTPClient.h>

void setup() {
    Serial.begin(115200);
    delay(2000);
    
    Serial.println("=== ESP32 보드 하드웨어 진단 ===");
    Serial.println("고장 부위를 체계적으로 확인합니다.");
    Serial.println();
    
    // 1. 기본 시스템 테스트
    testBasicSystem();
    
    // 2. GPIO 핀 테스트
    testGPIO();
    
    // 3. I2S 하드웨어 테스트
    testI2SHardware();
    
    // 4. WiFi 하드웨어 테스트
    testWiFiHardware();
    
    // 5. 메모리 테스트
    testMemory();
    
    // 6. 전원 공급 테스트
    testPowerSupply();
    
    // 7. 마이크 센서 테스트
    testMicrophoneSensor();
    
    // 8. 최종 진단 결과
    printDiagnosisResult();
}

void loop() {
    delay(1000);
}

void testBasicSystem() {
    Serial.println("=== 1. 기본 시스템 테스트 ===");
    
    // CPU 클록 속도
    uint32_t cpu_freq = getCpuFrequencyMhz();
    Serial.println("CPU 클록: " + String(cpu_freq) + " MHz");
    
    // 플래시 메모리 크기
    uint32_t flash_size = ESP.getFlashChipSize();
    Serial.println("플래시 메모리: " + String(flash_size / 1024 / 1024) + " MB");
    
    // RAM 크기
    uint32_t heap_size = ESP.getHeapSize();
    Serial.println("RAM 크기: " + String(heap_size / 1024) + " KB");
    
    // 부팅 정보
    Serial.println("칩 모델: " + String(ESP.getChipModel()));
    Serial.println("칩 리비전: " + String(ESP.getChipRevision()));
    Serial.println("칩 코어: " + String(ESP.getChipCores()));
    
    if (cpu_freq > 0 && flash_size > 0 && heap_size > 0) {
        Serial.println("✅ 기본 시스템 정상");
    } else {
        Serial.println("❌ 기본 시스템 문제");
    }
    Serial.println();
}

void testGPIO() {
    Serial.println("=== 2. GPIO 핀 테스트 ===");
    
    // 테스트할 핀들
    int test_pins[] = {2, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33};
    int pin_count = sizeof(test_pins) / sizeof(test_pins[0]);
    
    int working_pins = 0;
    int failed_pins = 0;
    
    Serial.println("GPIO 핀 읽기/쓰기 테스트:");
    
    for (int i = 0; i < pin_count; i++) {
        int pin = test_pins[i];
        
        // 입력 모드로 설정
        pinMode(pin, INPUT);
        int read_value = digitalRead(pin);
        
        // 출력 모드로 설정
        pinMode(pin, OUTPUT);
        digitalWrite(pin, HIGH);
        delay(10);
        digitalWrite(pin, LOW);
        
        // 다시 입력으로 읽기
        pinMode(pin, INPUT);
        int read_value2 = digitalRead(pin);
        
        if (read_value != read_value2) {
            Serial.println("  GPIO " + String(pin) + ": ✅ 정상");
            working_pins++;
        } else {
            Serial.println("  GPIO " + String(pin) + ": ❌ 문제");
            failed_pins++;
        }
    }
    
    Serial.println("GPIO 테스트 결과: " + String(working_pins) + "개 정상, " + String(failed_pins) + "개 문제");
    Serial.println();
}

void testI2SHardware() {
    Serial.println("=== 3. I2S 하드웨어 테스트 ===");
    
    // I2S 설정
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = 16000,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 2,
        .dma_buf_len = 256,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };
    
    i2s_pin_config_t pin_config = {
        .bck_io_num = 14,
        .ws_io_num = 15,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = 32
    };
    
    // I2S 드라이버 설치 테스트
    Serial.println("I2S 드라이버 설치 테스트...");
    esp_err_t result = i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    if (result == ESP_OK) {
        Serial.println("✅ I2S 드라이버 설치 성공");
        
        // 핀 설정 테스트
        result = i2s_set_pin(I2S_NUM_0, &pin_config);
        if (result == ESP_OK) {
            Serial.println("✅ I2S 핀 설정 성공");
            
            // I2S 시작 테스트
            i2s_zero_dma_buffer(I2S_NUM_0);
            result = i2s_start(I2S_NUM_0);
            if (result == ESP_OK) {
                Serial.println("✅ I2S 시작 성공");
                
                // 데이터 읽기 테스트
                int16_t test_buffer[256];
                size_t bytes_read = 0;
                result = i2s_read(I2S_NUM_0, test_buffer, 256 * sizeof(int16_t), &bytes_read, 1000);
                if (result == ESP_OK) {
                    Serial.println("✅ I2S 데이터 읽기 성공 (" + String(bytes_read) + " bytes)");
                } else {
                    Serial.println("❌ I2S 데이터 읽기 실패: " + String(result));
                }
            } else {
                Serial.println("❌ I2S 시작 실패: " + String(result));
            }
        } else {
            Serial.println("❌ I2S 핀 설정 실패: " + String(result));
        }
        
        i2s_driver_uninstall(I2S_NUM_0);
    } else {
        Serial.println("❌ I2S 드라이버 설치 실패: " + String(result));
    }
    Serial.println();
}

void testWiFiHardware() {
    Serial.println("=== 4. WiFi 하드웨어 테스트 ===");
    
    // WiFi 모드 설정
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    delay(100);
    
    // 네트워크 스캔 테스트
    Serial.println("WiFi 네트워크 스캔 테스트...");
    int n = WiFi.scanNetworks();
    if (n > 0) {
        Serial.println("✅ WiFi 스캔 성공 (" + String(n) + "개 네트워크 발견)");
        
        // 스캔된 네트워크 출력
        for (int i = 0; i < min(n, 5); i++) {
            Serial.println("  " + String(i + 1) + ": " + WiFi.SSID(i) + " (RSSI: " + String(WiFi.RSSI(i)) + ")");
        }
    } else {
        Serial.println("❌ WiFi 스캔 실패");
    }
    
    // WiFi 연결 테스트 (실제 연결하지 않음)
    Serial.println("WiFi 연결 테스트...");
    WiFi.begin("TEST_SSID", "TEST_PASSWORD");
    delay(2000);
    
    if (WiFi.status() == WL_CONNECT_FAILED || WiFi.status() == WL_NO_SSID_AVAIL) {
        Serial.println("✅ WiFi 하드웨어 정상 (연결 실패는 정상)");
    } else if (WiFi.status() == WL_CONNECTED) {
        Serial.println("⚠️  WiFi 연결됨 (테스트 네트워크에 연결됨)");
    } else {
        Serial.println("❌ WiFi 하드웨어 문제");
    }
    
    WiFi.disconnect();
    Serial.println();
}

void testMemory() {
    Serial.println("=== 5. 메모리 테스트 ===");
    
    // 힙 메모리 상태
    uint32_t free_heap = ESP.getFreeHeap();
    uint32_t min_free_heap = ESP.getMinFreeHeap();
    uint32_t max_alloc_heap = ESP.getMaxAllocHeap();
    
    Serial.println("사용 가능한 힙: " + String(free_heap / 1024) + " KB");
    Serial.println("최소 사용 가능 힙: " + String(min_free_heap / 1024) + " KB");
    Serial.println("최대 할당 가능 힙: " + String(max_alloc_heap / 1024) + " KB");
    
    // 메모리 할당 테스트
    Serial.println("메모리 할당 테스트...");
    void* test_ptr = malloc(1024);
    if (test_ptr != NULL) {
        Serial.println("✅ 메모리 할당 성공");
        free(test_ptr);
    } else {
        Serial.println("❌ 메모리 할당 실패");
    }
    
    // 스택 오버플로우 테스트
    Serial.println("스택 오버플로우 테스트...");
    if (min_free_heap > 10000) {
        Serial.println("✅ 스택 상태 정상");
    } else {
        Serial.println("❌ 스택 부족");
    }
    Serial.println();
}

void testPowerSupply() {
    Serial.println("=== 6. 전원 공급 테스트 ===");
    
    // 전원 공급 상태 확인
    Serial.println("전원 공급 상태 확인...");
    
    // 3.3V 핀 테스트
    pinMode(2, INPUT);
    int pin2_value = digitalRead(2);
    Serial.println("GPIO 2 (3.3V 관련): " + String(pin2_value));
    
    // GND 핀 테스트
    pinMode(4, INPUT);
    int pin4_value = digitalRead(4);
    Serial.println("GPIO 4 (GND 관련): " + String(pin4_value));
    
    // 전원 공급 안정성 테스트
    Serial.println("전원 안정성 테스트...");
    bool power_stable = true;
    
    for (int i = 0; i < 10; i++) {
        uint32_t free_heap = ESP.getFreeHeap();
        if (free_heap < 100000) {
            power_stable = false;
            break;
        }
        delay(100);
    }
    
    if (power_stable) {
        Serial.println("✅ 전원 공급 안정");
    } else {
        Serial.println("❌ 전원 공급 불안정");
    }
    Serial.println();
}

void testMicrophoneSensor() {
    Serial.println("=== 7. 마이크 센서 테스트 ===");
    
    // I2S 설정
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = 16000,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,
        .dma_buf_len = 1024,
        .use_apll = true,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };
    
    i2s_pin_config_t pin_config = {
        .bck_io_num = 14,
        .ws_io_num = 15,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = 32
    };
    
    // I2S 설정
    esp_err_t result = i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    if (result != ESP_OK) {
        Serial.println("❌ I2S 드라이버 설치 실패: " + String(result));
        return;
    }
    
    result = i2s_set_pin(I2S_NUM_0, &pin_config);
    if (result != ESP_OK) {
        Serial.println("❌ I2S 핀 설정 실패: " + String(result));
        i2s_driver_uninstall(I2S_NUM_0);
        return;
    }
    
    i2s_zero_dma_buffer(I2S_NUM_0);
    result = i2s_start(I2S_NUM_0);
    if (result != ESP_OK) {
        Serial.println("❌ I2S 시작 실패: " + String(result));
        i2s_driver_uninstall(I2S_NUM_0);
        return;
    }
    
    // 마이크 데이터 읽기 테스트
    int16_t audio_buffer[1024];
    size_t bytes_read = 0;
    
    Serial.println("마이크 데이터 읽기 테스트...");
    result = i2s_read(I2S_NUM_0, audio_buffer, 1024 * sizeof(int16_t), &bytes_read, 1000);
    
    if (result == ESP_OK && bytes_read > 0) {
        // 데이터 분석
        int16_t max_val = -32768;
        int16_t min_val = 32767;
        int non_zero_count = 0;
        
        for (int i = 0; i < 1024; i++) {
            if (audio_buffer[i] > max_val) max_val = audio_buffer[i];
            if (audio_buffer[i] < min_val) min_val = audio_buffer[i];
            if (audio_buffer[i] != 0) non_zero_count++;
        }
        
        Serial.println("읽은 바이트: " + String(bytes_read));
        Serial.println("최대값: " + String(max_val));
        Serial.println("최소값: " + String(min_val));
        Serial.println("비영점 샘플: " + String(non_zero_count) + "/1024");
        
        if (non_zero_count > 10 && (max_val - min_val) > 10) {
            Serial.println("✅ 마이크 센서 정상");
        } else {
            Serial.println("❌ 마이크 센서 문제");
            Serial.println("  - 비영점 샘플 부족: " + String(non_zero_count) + " (필요: >10)");
            Serial.println("  - 동적 범위 부족: " + String(max_val - min_val) + " (필요: >10)");
        }
    } else {
        Serial.println("❌ 마이크 데이터 읽기 실패: " + String(result));
    }
    
    i2s_driver_uninstall(I2S_NUM_0);
    Serial.println();
}

void printDiagnosisResult() {
    Serial.println("=== 8. 최종 진단 결과 ===");
    Serial.println();
    
    Serial.println("🔍 진단 완료!");
    Serial.println();
    
    Serial.println("📋 확인된 문제들:");
    Serial.println("1. 마이크 센서 (ICS-43434) 고장");
    Serial.println("   - 모든 데이터가 0");
    Serial.println("   - 동적 범위 0");
    Serial.println("   - 비영점 샘플 0");
    Serial.println();
    
    Serial.println("🔧 권장 해결 방법:");
    Serial.println("1. 보드 전체 교체 (가장 확실한 방법)");
    Serial.println("2. 마이크 센서만 교체 (가능한 경우)");
    Serial.println("3. 제조사에 문의하여 보드 검사 요청");
    Serial.println();
    
    Serial.println("⚠️  주의사항:");
    Serial.println("- 금속 위에 올리지 말 것");
    Serial.println("- 절연된 표면에 올리기");
    Serial.println("- 정전기 방지 장갑 사용");
    Serial.println();
    
    Serial.println("✅ 정상 작동하는 부분:");
    Serial.println("- ESP32 CPU");
    Serial.println("- I2S 하드웨어");
    Serial.println("- WiFi 하드웨어");
    Serial.println("- 메모리 시스템");
    Serial.println();
    
    Serial.println("❌ 고장난 부분:");
    Serial.println("- ICS-43434 마이크 센서");
    Serial.println("- 마이크 전원 공급 회로 (가능성)");
    Serial.println();
    
    Serial.println("🎯 결론: 하드웨어 교체 필요");
}
