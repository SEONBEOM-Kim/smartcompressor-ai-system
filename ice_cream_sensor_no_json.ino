#include <Arduino.h>
#include <driver/i2s.h>
#include <WiFi.h>
#include <HTTPClient.h>

// ====== 설정 ======
#define SAMPLE_RATE 16000  // 더 높은 샘플레이트
#define WINDOW_MS 1000     // 1초 윈도우
#define ANALYSIS_MS 5000   // 5초마다 분석
#define UPLOAD_MS 10000    // 10초마다 업로드
#define BUFFER_SIZE (SAMPLE_RATE * WINDOW_MS / 1000)

// 핀 설정
#define BOOT_BUTTON 0
#define LED_PIN 2
#define STATUS_LED 4

// WiFi 설정
const char* ssid = "U+Net98A4";
const char* password = "EF#AE96H86";
const char* serverURL = "http://3.39.124.0:3000/api/esp32/features";

// ====== 전역 변수 ======
int16_t audioBuffer[BUFFER_SIZE];
bool wifiConnected = false;
bool uploadEnabled = true;
unsigned long lastUpload = 0;
unsigned long lastAnalysis = 0;
String deviceID = "ICE_STORE_24H_" + String(random(1000, 9999));

// 버튼 제어
bool lastButtonState = HIGH;
unsigned long lastButtonPress = 0;

// 오디오 특징 구조체
struct AudioFeatures {
    uint32_t timestamp;
    float rms_energy;
    float spectral_centroid;
    float spectral_rolloff;
    float zero_crossing_rate;
    float mfcc[13];
    float compressor_state;
    float anomaly_score;
    float temperature_estimate;
    float efficiency_score;
};

// I2S 설정
const i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = (i2s_comm_format_t)(I2S_COMM_FORMAT_I2S | I2S_COMM_FORMAT_I2S_MSB),
    .intr_alloc_flags = 0,
    .dma_buf_count = 8,
    .dma_buf_len = 256,
    .use_apll = true,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
};

const i2s_pin_config_t pin_config = {
    .bck_io_num = 27, .ws_io_num = 25, .data_out_num = I2S_PIN_NO_CHANGE, .data_in_num = 26
};

// ====== 함수들 ======
void setupI2S() {
    pinMode(26, INPUT); pinMode(25, OUTPUT); pinMode(27, OUTPUT);
    i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_NUM_0, &pin_config);
    i2s_zero_dma_buffer(I2S_NUM_0);
    Serial.println("I2S ready");
}

void connectWiFi() {
    Serial.println("WiFi connecting...");
    WiFi.mode(WIFI_STA);
    WiFi.setAutoReconnect(true);
    WiFi.persistent(true);
    WiFi.disconnect();
    delay(100);
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(1000);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi connected! IP: " + WiFi.localIP().toString());
        wifiConnected = true;
    } else {
        Serial.println("\nWiFi failed!");
        wifiConnected = false;
    }
}

// 오디오 데이터 수집
bool collectAudio() {
    size_t bytes_read = 0;
    if (i2s_read(I2S_NUM_0, audioBuffer, BUFFER_SIZE * sizeof(int16_t), &bytes_read, portMAX_DELAY) == ESP_OK && bytes_read > 0) {
        return true;
    }
    return false;
}

// RMS 에너지 계산
float calculateRMS(int16_t* buffer, int length) {
    long sum = 0;
    for (int i = 0; i < length; i++) {
        sum += (long)buffer[i] * buffer[i];
    }
    return sqrt((float)sum / length);
}

// 제로 크로싱 비율 계산
float calculateZeroCrossingRate(int16_t* buffer, int length) {
    int crossings = 0;
    for (int i = 1; i < length; i++) {
        if ((buffer[i] >= 0) != (buffer[i-1] >= 0)) {
            crossings++;
        }
    }
    return (float)crossings / (length - 1);
}

// 스펙트럼 중심 계산 (단순화된 버전)
float calculateSpectralCentroid(int16_t* buffer, int length) {
    float sum = 0;
    float weightedSum = 0;
    
    for (int i = 0; i < length; i++) {
        float magnitude = abs(buffer[i]);
        sum += magnitude;
        weightedSum += magnitude * i;
    }
    
    return sum > 0 ? weightedSum / sum : 0;
}

// 스펙트럼 롤오프 계산 (단순화된 버전)
float calculateSpectralRolloff(int16_t* buffer, int length) {
    float totalEnergy = 0;
    for (int i = 0; i < length; i++) {
        totalEnergy += abs(buffer[i]);
    }
    
    float cumulativeEnergy = 0;
    for (int i = 0; i < length; i++) {
        cumulativeEnergy += abs(buffer[i]);
        if (cumulativeEnergy >= totalEnergy * 0.85) {
            return (float)i / length;
        }
    }
    return 1.0;
}

// MFCC 계산 (단순화된 버전)
void calculateMFCC(int16_t* buffer, int length, float* mfcc) {
    float rms = calculateRMS(buffer, length);
    
    for (int i = 0; i < 13; i++) {
        mfcc[i] = rms * (i + 1) * 0.1; // 단순화된 MFCC
    }
}

// 압축기 상태 감지
bool detectCompressorState(float rms, float spectralCentroid, float zeroCrossingRate) {
    bool isOn = (rms > 1000) && (spectralCentroid > 0.3) && (zeroCrossingRate < 0.1);
    return isOn;
}

// 이상 점수 계산
float calculateAnomalyScore(float rms, float spectralCentroid, float zeroCrossingRate, bool compressorState) {
    float anomaly = 0;
    
    if (rms > 5000) anomaly += 0.3;
    if (spectralCentroid > 0.8) anomaly += 0.2;
    if (zeroCrossingRate > 0.5) anomaly += 0.2;
    
    if (compressorState && rms < 500) anomaly += 0.3;
    if (!compressorState && rms > 2000) anomaly += 0.3;
    
    return min(anomaly, 1.0);
}

// 온도 추정
float estimateTemperature(float rms, float spectralCentroid) {
    float temp = 20.0;
    if (rms > 2000) temp += 5.0;
    if (spectralCentroid > 0.5) temp += 3.0;
    return temp;
}

// 효율성 점수 계산
float calculateEfficiencyScore(bool compressorState, float rms, float anomalyScore) {
    if (!compressorState) return 1.0;
    
    float efficiency = 1.0;
    if (rms > 3000) efficiency -= 0.2;
    if (anomalyScore > 0.5) efficiency -= 0.3;
    
    return max(efficiency, 0.0);
}

// 오디오 특징 추출
AudioFeatures extractAudioFeatures() {
    AudioFeatures features;
    features.timestamp = millis();
    
    features.rms_energy = calculateRMS(audioBuffer, BUFFER_SIZE);
    features.spectral_centroid = calculateSpectralCentroid(audioBuffer, BUFFER_SIZE);
    features.spectral_rolloff = calculateSpectralRolloff(audioBuffer, BUFFER_SIZE);
    features.zero_crossing_rate = calculateZeroCrossingRate(audioBuffer, BUFFER_SIZE);
    
    calculateMFCC(audioBuffer, BUFFER_SIZE, features.mfcc);
    
    features.compressor_state = detectCompressorState(features.rms_energy, features.spectral_centroid, features.zero_crossing_rate) ? 1.0 : 0.0;
    features.anomaly_score = calculateAnomalyScore(features.rms_energy, features.spectral_centroid, features.zero_crossing_rate, features.compressor_state > 0.5);
    features.temperature_estimate = estimateTemperature(features.rms_energy, features.spectral_centroid);
    features.efficiency_score = calculateEfficiencyScore(features.compressor_state > 0.5, features.rms_energy, features.anomaly_score);
    
    return features;
}

// JSON 문자열 생성 (수동)
String createJSON(AudioFeatures features) {
    String json = "{";
    json += "\"device_id\":\"" + deviceID + "\",";
    json += "\"timestamp\":" + String(features.timestamp) + ",";
    json += "\"rms_energy\":" + String(features.rms_energy, 2) + ",";
    json += "\"spectral_centroid\":" + String(features.spectral_centroid, 3) + ",";
    json += "\"spectral_rolloff\":" + String(features.spectral_rolloff, 3) + ",";
    json += "\"zero_crossing_rate\":" + String(features.zero_crossing_rate, 3) + ",";
    json += "\"compressor_state\":" + String(features.compressor_state, 1) + ",";
    json += "\"anomaly_score\":" + String(features.anomaly_score, 3) + ",";
    json += "\"temperature_estimate\":" + String(features.temperature_estimate, 1) + ",";
    json += "\"efficiency_score\":" + String(features.efficiency_score, 3) + ",";
    json += "\"mfcc\":[";
    
    for (int i = 0; i < 13; i++) {
        json += String(features.mfcc[i], 3);
        if (i < 12) json += ",";
    }
    
    json += "]}";
    return json;
}

// 특징 데이터 업로드
void uploadFeatures(AudioFeatures features) {
    if (!uploadEnabled || !wifiConnected) return;
    
    Serial.println("=== FEATURES UPLOAD START ===");
    
    String jsonString = createJSON(features);
    
    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("X-Device-ID", deviceID);
    http.addHeader("X-Store-Type", "ice_cream_24h");
    
    int code = http.POST(jsonString);
    
    if (code > 0) {
        Serial.println("SUCCESS: Features uploaded - " + String(code));
        Serial.println("Data size: " + String(jsonString.length()) + " bytes");
    } else {
        Serial.println("FAILED: Features upload - " + String(code));
    }
    
    http.end();
    Serial.println("=== FEATURES UPLOAD END ===");
}

void handleBootButton() {
    bool currentButtonState = digitalRead(BOOT_BUTTON);
    
    if (currentButtonState == LOW && lastButtonState == HIGH) {
        lastButtonPress = millis();
    }
    
    if (currentButtonState == HIGH && lastButtonState == LOW) {
        unsigned long pressDuration = millis() - lastButtonPress;
        
        if (pressDuration < 2000) {
            uploadEnabled = !uploadEnabled;
            Serial.println("=== Upload " + String(uploadEnabled ? "ENABLED" : "DISABLED") + " ===");
        } else if (pressDuration >= 3000) {
            Serial.println("=== WiFi Reconnecting ===");
            WiFi.disconnect();
            delay(1000);
            connectWiFi();
        }
    }
    
    lastButtonState = currentButtonState;
}

// ====== Arduino 필수 함수들 ======
void setup() {
    Serial.begin(115200);
    delay(2000);
    
    pinMode(BOOT_BUTTON, INPUT_PULLUP);
    pinMode(LED_PIN, OUTPUT);
    pinMode(STATUS_LED, OUTPUT);
    
    Serial.println("=== 24H Ice Cream Store Monitoring System ===");
    Serial.println("Device: " + deviceID);
    Serial.println("Feature-based data transmission mode");
    Serial.println("Compressor On/Off time series analysis");
    
    setupI2S();
    connectWiFi();
    
    Serial.println("System ready");
}

void loop() {
    handleBootButton();
    
    wifiConnected = (WiFi.status() == WL_CONNECTED);
    if (!wifiConnected) {
        connectWiFi();
    }
    
    // 오디오 수집
    if (collectAudio()) {
        // 5초마다 특징 분석
        if (millis() - lastAnalysis >= ANALYSIS_MS) {
            AudioFeatures features = extractAudioFeatures();
            
            // 특징 출력
            Serial.println("=== AUDIO FEATURES ===");
            Serial.println("RMS: " + String(features.rms_energy, 2));
            Serial.println("Spectral Centroid: " + String(features.spectral_centroid, 3));
            Serial.println("Compressor State: " + String(features.compressor_state > 0.5 ? "ON" : "OFF"));
            Serial.println("Anomaly Score: " + String(features.anomaly_score, 3));
            Serial.println("Temperature Est: " + String(features.temperature_estimate, 1) + "C");
            Serial.println("Efficiency: " + String(features.efficiency_score, 3));
            
            lastAnalysis = millis();
        }
        
        // 10초마다 업로드
        if (millis() - lastUpload >= UPLOAD_MS) {
            if (uploadEnabled && wifiConnected) {
                AudioFeatures features = extractAudioFeatures();
                uploadFeatures(features);
                lastUpload = millis();
            }
        }
    }
    
    // LED 상태 표시
    digitalWrite(LED_PIN, uploadEnabled ? HIGH : LOW);
    digitalWrite(STATUS_LED, wifiConnected ? HIGH : LOW);
    
    delay(10);
}
