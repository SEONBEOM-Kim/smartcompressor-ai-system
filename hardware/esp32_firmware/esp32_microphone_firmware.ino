// ESP-32 MEMS 마이크 펌웨어
// Signalcraft 압축기 진단 시스템

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <driver/i2s.h>

// WiFi 설정
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// 서버 설정
const char* serverURL = "http://3.39.124.0:8000/api/audio/upload";

// I2S 설정
#define I2S_WS 25
#define I2S_SD 33
#define I2S_SCK 32
#define I2S_PORT I2S_NUM_0

// 오디오 설정
#define SAMPLE_RATE 16000
#define SAMPLE_SIZE 16
#define BUFFER_SIZE 1024

// 전역 변수
int16_t audioBuffer[BUFFER_SIZE];
bool isRecording = false;
unsigned long lastUploadTime = 0;
const unsigned long uploadInterval = 30000; // 30초마다 업로드

void setup() {
  Serial.begin(115200);
  
  // WiFi 연결
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("WiFi 연결 중...");
  }
  Serial.println("WiFi 연결됨!");
  Serial.print("IP 주소: ");
  Serial.println(WiFi.localIP());
  
  // I2S 초기화
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4,
    .dma_buf_len = BUFFER_SIZE,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
  };
  
  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD
  };
  
  i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_PORT, &pin_config);
  
  Serial.println("I2S 초기화 완료!");
  Serial.println("마이크 녹음 시작...");
  isRecording = true;
}

void loop() {
  if (isRecording) {
    // 오디오 데이터 읽기
    size_t bytesRead;
    i2s_read(I2S_PORT, audioBuffer, BUFFER_SIZE * sizeof(int16_t), &bytesRead, portMAX_DELAY);
    
    // 30초마다 서버로 업로드
    if (millis() - lastUploadTime >= uploadInterval) {
      uploadAudioData();
      lastUploadTime = millis();
    }
  }
  
  delay(10);
}

void uploadAudioData() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi 연결 끊어짐!");
    return;
  }
  
  HTTPClient http;
  http.begin(serverURL);
  http.addHeader("Content-Type", "application/octet-stream");
  http.addHeader("X-Device-ID", "ESP32_MIC_001");
  http.addHeader("X-Sample-Rate", String(SAMPLE_RATE));
  http.addHeader("X-Bits-Per-Sample", String(SAMPLE_SIZE));
  
  // 오디오 데이터를 바이트 배열로 변환
  uint8_t audioBytes[BUFFER_SIZE * sizeof(int16_t)];
  memcpy(audioBytes, audioBuffer, BUFFER_SIZE * sizeof(int16_t));
  
  int httpResponseCode = http.POST(audioBytes, BUFFER_SIZE * sizeof(int16_t));
  
  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("업로드 성공! 응답: " + response);
  } else {
    Serial.println("업로드 실패! 오류 코드: " + String(httpResponseCode));
  }
  
  http.end();
}

// 녹음 시작/중지 함수
void startRecording() {
  isRecording = true;
  Serial.println("녹음 시작!");
}

void stopRecording() {
  isRecording = false;
  Serial.println("녹음 중지!");
}

// WiFi 재연결 함수
void reconnectWiFi() {
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(1000);
      Serial.println("WiFi 재연결 중...");
    }
    Serial.println("WiFi 재연결됨!");
  }
}
