/*
 * Signalcraft ESP32 센서 펌웨어
 * Tesla 스타일 실시간 센서 데이터 수집
 * 
 * 기능:
 * - 마이크로폰 (I2S) 오디오 수집
 * - 온도 센서 (DS18B20)
 * - 진동 센서 (ADXL345)
 * - 전력 센서 (ACS712)
 * - WiFi 연결 및 데이터 전송
 * - OTA 펌웨어 업데이트
 */

#include <WiFi.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_ADXL345_U.h>
#include <HTTPClient.h>
#include <Update.h>
#include <esp_wifi.h>
#include <esp_bt.h>

// 센서 핀 정의
#define I2S_WS 25
#define I2S_SD 33
#define I2S_SCK 32
#define TEMP_PIN 4
#define POWER_PIN 34
#define LED_PIN 2

// I2S 설정
#define I2S_SAMPLE_RATE 16000
#define I2S_SAMPLE_BITS 16
#define I2S_CHANNELS 1
#define BUFFER_SIZE 1024

// 센서 객체
OneWire oneWire(TEMP_PIN);
DallasTemperature tempSensor(&oneWire);
Adafruit_ADXL345_Unified accel = Adafruit_ADXL345_Unified(12345);

// WiFi 설정
const char* ssid = "Signalcraft_IoT";
const char* password = "signalcraft2024";
const char* server_host = "signalcraft.kr";
const int server_port = 8080;

// WebSocket 클라이언트
WebSocketsClient webSocket;

// 센서 데이터 구조
struct SensorData {
  float temperature;
  float vibration_x;
  float vibration_y;
  float vibration_z;
  float power_consumption;
  int audio_level;
  unsigned long timestamp;
  String device_id;
};

// 전역 변수
SensorData sensorData;
bool isConnected = false;
unsigned long lastDataSend = 0;
unsigned long lastHeartbeat = 0;
const unsigned long DATA_SEND_INTERVAL = 1000; // 1초마다 데이터 전송
const unsigned long HEARTBEAT_INTERVAL = 30000; // 30초마다 하트비트

// 오디오 버퍼
int16_t audioBuffer[BUFFER_SIZE];
int audioBufferIndex = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("Signalcraft ESP32 센서 시작...");
  
  // LED 초기화
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  
  // 센서 초기화
  initializeSensors();
  
  // WiFi 연결
  connectToWiFi();
  
  // WebSocket 연결
  connectToWebSocket();
  
  // OTA 업데이트 설정
  setupOTA();
  
  Serial.println("시스템 초기화 완료");
}

void loop() {
  // WebSocket 이벤트 처리
  webSocket.loop();
  
  // 센서 데이터 수집
  collectSensorData();
  
  // 오디오 데이터 수집
  collectAudioData();
  
  // 데이터 전송
  if (millis() - lastDataSend >= DATA_SEND_INTERVAL) {
    sendSensorData();
    lastDataSend = millis();
  }
  
  // 하트비트 전송
  if (millis() - lastHeartbeat >= HEARTBEAT_INTERVAL) {
    sendHeartbeat();
    lastHeartbeat = millis();
  }
  
  // 연결 상태 확인
  if (!isConnected) {
    reconnect();
  }
  
  delay(10);
}

void initializeSensors() {
  Serial.println("센서 초기화 중...");
  
  // 온도 센서 초기화
  tempSensor.begin();
  Serial.println("온도 센서 초기화 완료");
  
  // 진동 센서 초기화
  if (!accel.begin()) {
    Serial.println("진동 센서 초기화 실패!");
    while (1);
  }
  accel.setRange(ADXL345_RANGE_16_G);
  Serial.println("진동 센서 초기화 완료");
  
  // I2S 초기화
  i2s_install();
  i2s_set_pin();
  i2s_start();
  Serial.println("I2S 오디오 초기화 완료");
  
  // 전력 센서 핀 설정
  pinMode(POWER_PIN, INPUT);
  
  Serial.println("모든 센서 초기화 완료");
}

void i2s_install() {
  const i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = I2S_SAMPLE_RATE,
    .bits_per_sample = I2S_SAMPLE_BITS,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_STAND_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 4,
    .dma_buf_len = BUFFER_SIZE,
    .use_apll = false,
    .tx_desc_auto_clear = false,
    .fixed_mclk = 0
  };
  
  i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
}

void i2s_set_pin() {
  const i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD
  };
  
  i2s_set_pin(I2S_NUM_0, &pin_config);
}

void i2s_start() {
  i2s_start(I2S_NUM_0);
}

void connectToWiFi() {
  WiFi.begin(ssid, password);
  Serial.print("WiFi 연결 중");
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println();
    Serial.println("WiFi 연결 성공!");
    Serial.print("IP 주소: ");
    Serial.println(WiFi.localIP());
    digitalWrite(LED_PIN, HIGH);
  } else {
    Serial.println();
    Serial.println("WiFi 연결 실패!");
    digitalWrite(LED_PIN, LOW);
  }
}

void connectToWebSocket() {
  webSocket.begin(server_host, server_port, "/ws/sensors");
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);
}

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_DISCONNECTED:
      Serial.println("WebSocket 연결 끊김");
      isConnected = false;
      digitalWrite(LED_PIN, LOW);
      break;
      
    case WStype_CONNECTED:
      Serial.println("WebSocket 연결 성공!");
      isConnected = true;
      digitalWrite(LED_PIN, HIGH);
      sendDeviceInfo();
      break;
      
    case WStype_TEXT:
      handleWebSocketMessage((char*)payload);
      break;
      
    case WStype_ERROR:
      Serial.println("WebSocket 오류");
      isConnected = false;
      break;
      
    default:
      break;
  }
}

void handleWebSocketMessage(char* message) {
  DynamicJsonDocument doc(1024);
  deserializeJson(doc, message);
  
  String type = doc["type"];
  
  if (type == "config") {
    // 센서 설정 업데이트
    updateSensorConfig(doc);
  } else if (type == "firmware_update") {
    // 펌웨어 업데이트 요청
    handleFirmwareUpdate(doc);
  } else if (type == "calibrate") {
    // 센서 캘리브레이션
    calibrateSensors();
  }
}

void collectSensorData() {
  // 온도 데이터 수집
  tempSensor.requestTemperatures();
  sensorData.temperature = tempSensor.getTempCByIndex(0);
  
  // 진동 데이터 수집
  sensors_event_t event;
  accel.getEvent(&event);
  sensorData.vibration_x = event.acceleration.x;
  sensorData.vibration_y = event.acceleration.y;
  sensorData.vibration_z = event.acceleration.z;
  
  // 전력 소비량 측정
  int powerRaw = analogRead(POWER_PIN);
  sensorData.power_consumption = map(powerRaw, 0, 4095, 0, 100); // 0-100%로 변환
  
  // 타임스탬프
  sensorData.timestamp = millis();
  
  // 디바이스 ID
  sensorData.device_id = WiFi.macAddress();
}

void collectAudioData() {
  size_t bytesRead = 0;
  esp_err_t result = i2s_read(I2S_NUM_0, &audioBuffer[audioBufferIndex], 
                             sizeof(int16_t), &bytesRead, portMAX_DELAY);
  
  if (result == ESP_OK && bytesRead > 0) {
    audioBufferIndex++;
    
    if (audioBufferIndex >= BUFFER_SIZE) {
      // 오디오 레벨 계산
      long sum = 0;
      for (int i = 0; i < BUFFER_SIZE; i++) {
        sum += abs(audioBuffer[i]);
      }
      sensorData.audio_level = sum / BUFFER_SIZE;
      
      // 버퍼 리셋
      audioBufferIndex = 0;
    }
  }
}

void sendSensorData() {
  if (!isConnected) return;
  
  DynamicJsonDocument doc(1024);
  doc["type"] = "sensor_data";
  doc["device_id"] = sensorData.device_id;
  doc["timestamp"] = sensorData.timestamp;
  doc["temperature"] = sensorData.temperature;
  doc["vibration"] = {
    "x": sensorData.vibration_x,
    "y": sensorData.vibration_y,
    "z": sensorData.vibration_z
  };
  doc["power_consumption"] = sensorData.power_consumption;
  doc["audio_level"] = sensorData.audio_level;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  webSocket.sendTXT(jsonString);
}

void sendHeartbeat() {
  if (!isConnected) return;
  
  DynamicJsonDocument doc(512);
  doc["type"] = "heartbeat";
  doc["device_id"] = sensorData.device_id;
  doc["timestamp"] = millis();
  doc["uptime"] = millis();
  doc["free_heap"] = ESP.getFreeHeap();
  doc["wifi_rssi"] = WiFi.RSSI();
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  webSocket.sendTXT(jsonString);
}

void sendDeviceInfo() {
  DynamicJsonDocument doc(1024);
  doc["type"] = "device_info";
  doc["device_id"] = WiFi.macAddress();
  doc["firmware_version"] = "1.0.0";
  doc["hardware_version"] = "ESP32_v1";
  doc["sensors"] = {
    "microphone": true,
    "temperature": true,
    "vibration": true,
    "power": true
  };
  doc["capabilities"] = {
    "ota_update": true,
    "real_time_streaming": true,
    "calibration": true
  };
  
  String jsonString;
  serializeJson(doc, jsonString);
  webSocket.sendTXT(jsonString);
}

void updateSensorConfig(DynamicJsonDocument& config) {
  // 센서 설정 업데이트 로직
  if (config.containsKey("sample_rate")) {
    // 샘플링 레이트 변경
  }
  if (config.containsKey("sensitivity")) {
    // 센서 민감도 변경
  }
}

void calibrateSensors() {
  Serial.println("센서 캘리브레이션 시작...");
  
  // 진동 센서 캘리브레이션
  accel.setRange(ADXL345_RANGE_2_G);
  delay(1000);
  accel.setRange(ADXL345_RANGE_16_G);
  
  // 전력 센서 캘리브레이션
  // 0W 상태에서 기준값 설정
  
  Serial.println("센서 캘리브레이션 완료");
}

void setupOTA() {
  // OTA 업데이트 설정
  ArduinoOTA.setHostname("Signalcraft-ESP32");
  ArduinoOTA.setPassword("signalcraft2024");
  
  ArduinoOTA.onStart([]() {
    String type = (ArduinoOTA.getCommand() == U_FLASH) ? "sketch" : "filesystem";
    Serial.println("OTA 업데이트 시작: " + type);
  });
  
  ArduinoOTA.onEnd([]() {
    Serial.println("OTA 업데이트 완료");
  });
  
  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("진행률: %u%%\r", (progress / (total / 100)));
  });
  
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("OTA 오류[%u]: ", error);
    if (error == OTA_AUTH_ERROR) Serial.println("인증 실패");
    else if (error == OTA_BEGIN_ERROR) Serial.println("시작 실패");
    else if (error == OTA_CONNECT_ERROR) Serial.println("연결 실패");
    else if (error == OTA_RECEIVE_ERROR) Serial.println("수신 실패");
    else if (error == OTA_END_ERROR) Serial.println("완료 실패");
  });
  
  ArduinoOTA.begin();
}

void handleFirmwareUpdate(DynamicJsonDocument& updateInfo) {
  String firmwareUrl = updateInfo["firmware_url"];
  String version = updateInfo["version"];
  
  Serial.println("펌웨어 업데이트 시작: " + version);
  
  HTTPClient http;
  http.begin(firmwareUrl);
  
  int httpCode = http.GET();
  if (httpCode == HTTP_CODE_OK) {
    int contentLength = http.getSize();
    if (contentLength > 0) {
      WiFiClient* stream = http.getStreamPtr();
      if (Update.begin(contentLength)) {
        Update.writeStream(*stream);
        if (Update.end()) {
          Serial.println("펌웨어 업데이트 완료, 재시작 중...");
          ESP.restart();
        } else {
          Serial.println("펌웨어 업데이트 실패");
        }
      }
    }
  }
  
  http.end();
}

void reconnect() {
  if (WiFi.status() != WL_CONNECTED) {
    connectToWiFi();
  }
  
  if (!isConnected) {
    connectToWebSocket();
  }
}
