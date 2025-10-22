/*
 * ICS-43434 마이크 테스트 코드 v2
 * 철판 쇼트 문제 해결용
 */

#include <driver/i2s.h>

// ICS-43434 마이크 핀 설정 (테스트에서 작동했던 핀)
#define I2S_WS_PIN 15      // Word Select
#define I2S_BCK_PIN 14     // Bit Clock  
#define I2S_DATA_PIN 32    // Data

#define SAMPLE_RATE 16000
#define BUFFER_SIZE 1024

int16_t audioBuffer[BUFFER_SIZE];

void setup() {
    Serial.begin(115200);
    delay(2000);
    
    Serial.println("=== ICS-43434 마이크 테스트 v2 ===");
    Serial.println("⚠️  주의: 절연된 표면에 올려놓으세요!");
    Serial.println("   - 플라스틱 받침 사용");
    Serial.println("   - 종이 또는 카드보드 위에");
    Serial.println("   - 절연 테이프 사용");
    Serial.println();
    
    // 핀 연결 가이드
    printConnectionGuide();
    
    // I2S 설정
    setupI2S();
    
    // 핀 테스트
    testPins();
    
    Serial.println("\n=== 테스트 시작 ===");
}

void loop() {
    Serial.println("\n--- 마이크 데이터 읽기 ---");
    
    if (collectAudio()) {
        analyzeAudio();
    } else {
        Serial.println("❌ 데이터 읽기 실패");
        Serial.println("   → 절연 상태 확인 필요");
    }
    
    delay(2000);
}

void printConnectionGuide() {
    Serial.println("=== 핀 연결 가이드 ===");
    Serial.println("ICS-43434 → ESP32");
    Serial.println("VDD (1) → 3.3V (빨간색)");
    Serial.println("GND (2) → GND (검은색)");
    Serial.println("WS  (3) → GPIO 15 (노란색)");
    Serial.println("BCK (4) → GPIO 14 (초록색)");
    Serial.println("DATA(5) → GPIO 32 (파란색)");
    Serial.println();
    Serial.println("🔧 절연 방법:");
    Serial.println("1. 플라스틱 받침 사용");
    Serial.println("2. 종이/카드보드 위에 올리기");
    Serial.println("3. 절연 테이프로 보드 하단 덮기");
    Serial.println();
}

void setupI2S() {
    Serial.println("=== I2S 설정 ===");
    
    // 핀 모드 설정
    pinMode(I2S_WS_PIN, OUTPUT);
    pinMode(I2S_BCK_PIN, OUTPUT);
    pinMode(I2S_DATA_PIN, INPUT);
    Serial.println("✅ 핀 모드 설정 완료");
    
    // I2S 설정 (테스트에서 작동했던 설정)
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_STAND_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,    // 테스트에서 작동했던 설정
        .dma_buf_len = 1024,
        .use_apll = true,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };
    
    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_BCK_PIN,
        .ws_io_num = I2S_WS_PIN,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = I2S_DATA_PIN
    };
    
    // I2S 드라이버 설치
    esp_err_t result = i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    if (result != ESP_OK) {
        Serial.println("❌ I2S 드라이버 설치 실패: " + String(result));
        return;
    }
    Serial.println("✅ I2S 드라이버 설치 성공");
    
    // 핀 설정
    result = i2s_set_pin(I2S_NUM_0, &pin_config);
    if (result != ESP_OK) {
        Serial.println("❌ I2S 핀 설정 실패: " + String(result));
        return;
    }
    Serial.println("✅ I2S 핀 설정 성공");
    
    // I2S 시작
    i2s_zero_dma_buffer(I2S_NUM_0);
    result = i2s_start(I2S_NUM_0);
    if (result != ESP_OK) {
        Serial.println("❌ I2S 시작 실패: " + String(result));
        return;
    }
    Serial.println("✅ I2S 시작 성공");
}

void testPins() {
    Serial.println("\n=== 핀 테스트 ===");
    
    // DATA 핀 초기 상태
    int data_initial = digitalRead(I2S_DATA_PIN);
    Serial.println("DATA 핀 초기 상태: " + String(data_initial));
    
    // WS 핀 테스트
    Serial.println("WS 핀 테스트...");
    for (int i = 0; i < 3; i++) {
        digitalWrite(I2S_WS_PIN, HIGH);
        delay(50);
        digitalWrite(I2S_WS_PIN, LOW);
        delay(50);
    }
    
    // BCK 핀 테스트
    Serial.println("BCK 핀 테스트...");
    for (int i = 0; i = 5; i++) {
        digitalWrite(I2S_BCK_PIN, HIGH);
        delay(10);
        digitalWrite(I2S_BCK_PIN, LOW);
        delay(10);
    }
    
    // DATA 핀 상태 재확인
    int data_after = digitalRead(I2S_DATA_PIN);
    Serial.println("DATA 핀 상태 (클록 후): " + String(data_after));
    
    if (data_initial != data_after) {
        Serial.println("✅ DATA 핀에 변화 감지됨");
    } else {
        Serial.println("❌ DATA 핀에 변화 없음");
        Serial.println("   → 절연 상태 또는 연결 확인 필요");
    }
}

bool collectAudio() {
    size_t bytes_read = 0;
    
    Serial.println("I2S에서 데이터 읽는 중...");
    esp_err_t result = i2s_read(I2S_NUM_0, audioBuffer, BUFFER_SIZE * sizeof(int16_t), &bytes_read, 1000);
    
    if (result != ESP_OK) {
        Serial.println("❌ I2S 읽기 오류: " + String(result));
        return false;
    }
    
    if (bytes_read == 0) {
        Serial.println("❌ 읽은 데이터 없음");
        return false;
    }
    
    Serial.println("✅ " + String(bytes_read) + " 바이트 읽기 성공");
    return true;
}

void analyzeAudio() {
    Serial.println("\n--- 오디오 데이터 분석 ---");
    
    int16_t max_val = -32768;
    int16_t min_val = 32767;
    int16_t non_zero_count = 0;
    int16_t positive_count = 0;
    int16_t negative_count = 0;
    long sum = 0;
    
    for (int i = 0; i < BUFFER_SIZE; i++) {
        if (audioBuffer[i] > max_val) max_val = audioBuffer[i];
        if (audioBuffer[i] < min_val) min_val = audioBuffer[i];
        if (audioBuffer[i] != 0) non_zero_count++;
        if (audioBuffer[i] > 0) positive_count++;
        if (audioBuffer[i] < 0) negative_count++;
        sum += abs(audioBuffer[i]);
    }
    
    float avg_amplitude = (float)sum / BUFFER_SIZE;
    int16_t range = max_val - min_val;
    
    Serial.println("최대값: " + String(max_val));
    Serial.println("최소값: " + String(min_val));
    Serial.println("범위: " + String(range));
    Serial.println("비영점 샘플: " + String(non_zero_count) + "/" + String(BUFFER_SIZE));
    Serial.println("양수 샘플: " + String(positive_count));
    Serial.println("음수 샘플: " + String(negative_count));
    Serial.println("평균 진폭: " + String(avg_amplitude, 2));
    
    // 첫 10개 샘플 출력
    Serial.print("첫 10개 샘플: ");
    for (int i = 0; i < 10; i++) {
        Serial.print(String(audioBuffer[i]));
        if (i < 9) Serial.print(", ");
    }
    Serial.println();
    
    // 마이크 상태 판정
    Serial.println("\n=== 마이크 상태 판정 ===");
    
    if (non_zero_count > 10 && range > 10) {
        Serial.println("✅ 마이크 정상 작동!");
        Serial.println("  - 충분한 비영점 샘플: " + String(non_zero_count));
        Serial.println("  - 좋은 동적 범위: " + String(range));
        
        if (positive_count > 0 && negative_count > 0) {
            Serial.println("  - 양수/음수 값 모두 존재");
        }
    } else {
        Serial.println("❌ 마이크 문제 발견!");
        if (non_zero_count <= 10) {
            Serial.println("  - 비영점 샘플 부족: " + String(non_zero_count) + " (필요: >10)");
        }
        if (range <= 10) {
            Serial.println("  - 동적 범위 부족: " + String(range) + " (필요: >10)");
        }
        Serial.println("해결 방법:");
        Serial.println("  1. 절연된 표면에 올리기");
        Serial.println("  2. 핀 연결 재확인");
        Serial.println("  3. 마이크 전원 확인");
    }
}
