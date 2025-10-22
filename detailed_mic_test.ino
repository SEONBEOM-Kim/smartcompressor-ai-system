/*
 * 상세한 ICS-43434 마이크 연결 테스트
 * 하드웨어 문제 진단용
 */

#include <driver/i2s.h>

// ICS-43434 마이크 핀 설정
#define I2S_WS_PIN 15      // Word Select
#define I2S_BCK_PIN 14     // Bit Clock  
#define I2S_DATA_PIN 32    // Data

#define SAMPLE_RATE 16000
#define BUFFER_SIZE 1024

int16_t audioBuffer[BUFFER_SIZE];

void setup() {
    Serial.begin(115200);
    delay(2000);
    
    Serial.println("=== 상세한 ICS-43434 마이크 테스트 ===");
    Serial.println();
    
    // 1. 핀 연결 가이드
    printConnectionGuide();
    
    // 2. 핀 상태 확인
    checkPinStates();
    
    // 3. I2S 설정
    setupI2S();
    
    // 4. 클록 신호 테스트
    testClockSignals();
    
    Serial.println("\n=== 테스트 시작 ===");
}

void loop() {
    Serial.println("\n--- 마이크 데이터 읽기 ---");
    
    if (collectAudio()) {
        analyzeAudio();
        checkDataPatterns();
    } else {
        Serial.println("❌ 데이터 읽기 실패");
    }
    
    delay(3000);
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
    Serial.println("⚠️  중요: VDD는 반드시 3.3V여야 함!");
    Serial.println("⚠️  GND는 반드시 연결되어야 함!");
    Serial.println();
}

void checkPinStates() {
    Serial.println("=== 핀 상태 확인 ===");
    
    // 핀 모드 설정
    pinMode(I2S_WS_PIN, OUTPUT);
    pinMode(I2S_BCK_PIN, OUTPUT);
    pinMode(I2S_DATA_PIN, INPUT);
    
    // DATA 핀 초기 상태
    int data_initial = digitalRead(I2S_DATA_PIN);
    Serial.println("DATA 핀 초기 상태: " + String(data_initial));
    
    // WS 핀 테스트
    Serial.println("WS 핀 테스트 중...");
    for (int i = 0; i < 5; i++) {
        digitalWrite(I2S_WS_PIN, HIGH);
        delay(50);
        digitalWrite(I2S_WS_PIN, LOW);
        delay(50);
    }
    Serial.println("WS 핀 토글 완료");
    
    // BCK 핀 테스트
    Serial.println("BCK 핀 테스트 중...");
    for (int i = 0; i < 10; i++) {
        digitalWrite(I2S_BCK_PIN, HIGH);
        delay(10);
        digitalWrite(I2S_BCK_PIN, LOW);
        delay(10);
    }
    Serial.println("BCK 핀 토글 완료");
    
    // DATA 핀 상태 재확인
    int data_after = digitalRead(I2S_DATA_PIN);
    Serial.println("DATA 핀 상태 (클록 후): " + String(data_after));
    
    if (data_initial != data_after) {
        Serial.println("✅ DATA 핀에 변화 감지됨");
    } else {
        Serial.println("❌ DATA 핀에 변화 없음 - 연결 확인 필요");
    }
}

void setupI2S() {
    Serial.println("\n=== I2S 설정 ===");
    
    // I2S 설정
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = SAMPLE_RATE,
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
        .bck_io_num = I2S_BCK_PIN,
        .ws_io_num = I2S_WS_PIN,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = I2S_DATA_PIN
    };
    
    // 드라이버 설치
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

void testClockSignals() {
    Serial.println("\n=== 클록 신호 테스트 ===");
    
    // I2S가 시작되면 자동으로 클록 신호가 생성됨
    delay(100);
    
    // DATA 핀에서 변화 확인
    int samples[10];
    for (int i = 0; i < 10; i++) {
        samples[i] = digitalRead(I2S_DATA_PIN);
        delay(10);
    }
    
    Serial.print("DATA 핀 샘플: ");
    for (int i = 0; i < 10; i++) {
        Serial.print(String(samples[i]));
        if (i < 9) Serial.print(" ");
    }
    Serial.println();
    
    // 변화 확인
    bool has_variation = false;
    for (int i = 1; i < 10; i++) {
        if (samples[i] != samples[0]) {
            has_variation = true;
            break;
        }
    }
    
    if (has_variation) {
        Serial.println("✅ DATA 핀에 신호 변화 감지");
    } else {
        Serial.println("❌ DATA 핀에 신호 변화 없음");
        Serial.println("   → 마이크 전원 또는 연결 문제 가능성");
    }
}

bool collectAudio() {
    size_t bytes_read = 0;
    
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
}

void checkDataPatterns() {
    Serial.println("\n--- 데이터 패턴 분석 ---");
    
    // 첫 20개 샘플 출력
    Serial.print("첫 20개 샘플: ");
    for (int i = 0; i < 20; i++) {
        Serial.print(String(audioBuffer[i]));
        if (i < 19) Serial.print(", ");
    }
    Serial.println();
    
    // 연속된 0의 개수 확인
    int consecutive_zeros = 0;
    int max_consecutive_zeros = 0;
    
    for (int i = 0; i < BUFFER_SIZE; i++) {
        if (audioBuffer[i] == 0) {
            consecutive_zeros++;
            if (consecutive_zeros > max_consecutive_zeros) {
                max_consecutive_zeros = consecutive_zeros;
            }
        } else {
            consecutive_zeros = 0;
        }
    }
    
    Serial.println("최대 연속 0 개수: " + String(max_consecutive_zeros));
    
    // 진단 결과
    Serial.println("\n=== 진단 결과 ===");
    
    if (max_val == 0 && min_val == 0) {
        Serial.println("❌ 모든 데이터가 0입니다!");
        Serial.println("가능한 원인:");
        Serial.println("  1. 마이크 전원 공급 문제 (VDD 연결 확인)");
        Serial.println("  2. GND 연결 문제");
        Serial.println("  3. DATA 핀 연결 문제");
        Serial.println("  4. 마이크 자체 고장");
        Serial.println("  5. 잘못된 핀 연결");
    } else if (max_consecutive_zeros > BUFFER_SIZE * 0.8) {
        Serial.println("⚠️  대부분의 데이터가 0입니다!");
        Serial.println("마이크 전원 또는 연결에 문제가 있을 수 있습니다.");
    } else {
        Serial.println("✅ 마이크가 정상적으로 작동하고 있습니다!");
    }
}
