/*
 * esp32_cam.ino — Overhead Canopy Capture Firmware
 * Board: ESP32-S3 WROOM CAM (OV5640 / OV2640)
 * Description: Captures high-res top-down images of water spinach and uploads
 *              via HTTP multipart/form-data directly to FastAPI /predict
 */

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <esp_wifi.h>
#include "esp_camera.h"
#include "camera_pins.h"
#include "config.h"

unsigned long lastPollTime = 0;
unsigned long lastAutoCaptureTime = 0;

void initCamera() {
    camera_config_t config;
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sccb_sda = SIOD_GPIO_NUM;
    config.pin_sccb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;
    config.grab_mode = CAMERA_GRAB_LATEST;

    // Use high resolution if PSRAM is available
    if (psramFound()) {
        config.frame_size = FRAMESIZE_UXGA; // 1600x1200
        config.jpeg_quality = JPEG_QUALITY;
        config.fb_count = 2;
        config.fb_location = CAMERA_FB_IN_PSRAM;
        Serial.println("[CAM] PSRAM detected: Using UXGA (1600x1200) mode.");
    } else {
        config.frame_size = FRAMESIZE_SVGA; // 800x600 fallback
        config.jpeg_quality = 12;
        config.fb_count = 1;
        config.fb_location = CAMERA_FB_IN_DRAM;
        Serial.println("[CAM] PSRAM not found: Using SVGA mode.");
    }

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("[CAM ERROR] Camera init failed with error 0x%x\n", err);
        return;
    }
    Serial.println("[CAM] Camera sensor initialized successfully.");
}

void connectWiFi() {
    Serial.printf("[CAM] Connecting to Wi-Fi SSID: %s ", WIFI_SSID);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    unsigned long start = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - start < 10000) {
        delay(500);
        Serial.print(".");
    }

    if (WiFi.status() == WL_CONNECTED) {
        Serial.println(" CONNECTED!");
        Serial.print("[CAM] IP: ");
        Serial.println(WiFi.localIP());
    } else {
        Serial.println(" [TIMEOUT] WiFi failed.");
    }
}

bool captureAndUpload() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("[CAM] WiFi disconnected, skipping upload.");
        return false;
    }

    Serial.println("\n[CAM] Capturing top-down frame...");
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("[CAM ERROR] Failed to grab frame buffer.");
        return false;
    }

    Serial.printf("[CAM] Frame captured: %u bytes (%dx%d)\n", fb->len, fb->width, fb->height);

    HTTPClient http;
    http.begin(PREDICT_URL);

    String boundary = "----WebKitFormBoundaryHydroSyncESP32";
    http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);

    // Build multipart body header
    String head = "--" + boundary + "\r\n";
    head += "Content-Disposition: form-data; name=\"device_id\"\r\n\r\n";
    head += String(DEVICE_ID) + "\r\n";
    head += "--" + boundary + "\r\n";
    head += "Content-Disposition: form-data; name=\"image\"; filename=\"topdown.jpg\"\r\n";
    head += "Content-Type: image/jpeg\r\n\r\n";

    String tail = "\r\n--" + boundary + "--\r\n";

    size_t totalLen = head.length() + fb->len + tail.length();
    uint8_t* payload = (uint8_t*)malloc(totalLen);
    if (!payload) {
        Serial.println("[CAM ERROR] Failed to allocate memory for POST payload.");
        esp_camera_fb_return(fb);
        http.end();
        return false;
    }

    // Assemble payload buffer
    memcpy(payload, head.c_str(), head.length());
    memcpy(payload + head.length(), fb->buf, fb->len);
    memcpy(payload + head.length() + fb->len, tail.c_str(), tail.length());

    Serial.printf("[CAM] Sending %u bytes to %s ...\n", totalLen, PREDICT_URL);
    int httpResponseCode = http.POST(payload, totalLen);

    free(payload);
    esp_camera_fb_return(fb);

    if (httpResponseCode == 200) {
        String response = http.getString();
        Serial.printf("[CAM SUCCESS] Server response (200):\n%s\n", response.c_str());
        http.end();
        return true;
    } else {
        Serial.printf("[CAM ERROR] HTTP POST returned code: %d\n", httpResponseCode);
        http.end();
        return false;
    }
}

void pollRemoteCaptureCommand() {
    if (WiFi.status() != WL_CONNECTED) return;

    HTTPClient http;
    http.begin(URL_POLL_CAM_COMMAND);
    int code = http.GET();
    if (code == 200) {
        String payload = http.getString();
        StaticJsonDocument<256> doc;
        if (!deserializeJson(doc, payload)) {
            const char* cmd = doc["command"] | "";
            if (strcmp(cmd, "CAPTURE") == 0) {
                Serial.println("[REMOTE DASHBOARD] 'Capture Photo Now' command received!");
                captureAndUpload();
            }
        }
    }
    http.end();
}

void handleSerialCommands() {
    if (Serial.available() > 0) {
        String input = Serial.readStringUntil('\n');
        input.trim();
        input.toUpperCase();
        if (input == "CAPTURE" || input == "SNAP" || input == "PHOTO") {
            Serial.println("[SERIAL] Manual capture command triggered!");
            captureAndUpload();
        }
    }
}

void setup() {
    Serial.begin(115200);
    delay(1000);
    Serial.println("\n--- ESP32-S3 Overhead CAM Initialization ---");

    // Reduce CPU frequency from 240MHz down to 160MHz to prevent excessive heating
    setCpuFrequencyMhz(160);
    Serial.printf("[THERMAL CONTROL] CPU Clock adjusted to %d MHz (Cooler operation)\n", getCpuFrequencyMhz());

    initCamera();
    connectWiFi();

    // Enable WiFi power saving to keep RF chip cool when idle
    esp_wifi_set_ps(WIFI_PS_MIN_MODEM);

    // Initial capture on boot
    captureAndUpload();
    lastAutoCaptureTime = millis();
}

void loop() {
    unsigned long now = millis();
    handleSerialCommands();

    if (now - lastPollTime >= 1500) {
        lastPollTime = now;
        pollRemoteCaptureCommand();
    }

    if (now - lastAutoCaptureTime >= (unsigned long)CAPTURE_INTERVAL_S * 1000) {
        lastAutoCaptureTime = now;
        captureAndUpload();
    }

    // Yield CPU time so cores don't spin at 100% duty cycle (drastically cools the board)
    delay(30);
}
