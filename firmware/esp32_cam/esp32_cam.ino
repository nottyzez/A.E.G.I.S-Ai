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
#include <esp_sleep.h>
#include <Preferences.h>
#include "esp_camera.h"
#include "camera_pins.h"
#include "config.h"

// Fallbacks so a config.h copied before the sleep work still compiles.
#ifndef SLEEP_INTERVAL_S
#define SLEEP_INTERVAL_S 15
#endif
#ifndef CAM_SLEEP_ENABLED
#define CAM_SLEEP_ENABLED 1
#endif

unsigned long lastAutoCaptureTime = 0;
unsigned long lastRoundTime = 0;

// ------------------------------------------------------------------------------
// Runtime Config (NVS) — same serial commands as esp32_main.ino:
//   SET WIFI <ssid> <password>   SET SERVER <ip>   SHOW   RESET
// ------------------------------------------------------------------------------
Preferences prefs;
String cfgSsid = WIFI_SSID;
String cfgPass = WIFI_PASSWORD;
String cfgHost = SERVER_HOST;
String cfgPort = String(SERVER_PORT);

void loadRuntimeConfig() {
    prefs.begin("aegis", true);
    cfgSsid = prefs.getString("ssid", WIFI_SSID);
    cfgPass = prefs.getString("pass", WIFI_PASSWORD);
    cfgHost = prefs.getString("host", SERVER_HOST);
    cfgPort = prefs.getString("port", String(SERVER_PORT));
    prefs.end();
}

// Endpoints are built from the NVS values, so SET SERVER takes effect without
// a recompile. The old PREDICT_URL / URL_POLL_CAM_COMMAND macros baked
// SERVER_HOST in at compile time. The port is NVS too: a Droplet serves
// through Nginx on 80, not 8000.
String apiUrl(const char* path) {
    return String("http://") + cfgHost + ":" + cfgPort + path;
}

bool initCamera() {
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
    // WHEN_EMPTY stops the DMA once every buffer holds a frame. With LATEST the
    // driver overwrites continuously whenever nobody calls esp_camera_fb_get(),
    // which is exactly what "cam_hal: FB-OVF" in the log was reporting.
    config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;

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
        return false;
    }
    Serial.println("[CAM] Camera sensor initialized successfully.");
    return true;
}

void connectWiFi() {
    Serial.printf("[CAM] Connecting to Wi-Fi SSID: %s ", cfgSsid.c_str());
    WiFi.mode(WIFI_STA);
    WiFi.setAutoReconnect(true);
    WiFi.begin(cfgSsid.c_str(), cfgPass.c_str());

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

bool captureAndUpload(const char* mode) {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("[CAM] WiFi disconnected, skipping upload.");
        return false;
    }

    Serial.println("\n[CAM] Capturing top-down frame...");
    // The sensor's XCLK stops during light sleep, so the first buffer after a
    // wake can be a partial frame. Throw one away before the real capture.
    camera_fb_t* stale = esp_camera_fb_get();
    if (stale) esp_camera_fb_return(stale);

    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
        // After light sleep the sensor's clock has been stopped for a while;
        // a driver that fails to recover the DMA path needs a fresh init.
        Serial.println("[CAM] Frame grab failed after wake, re-initialising camera...");
        esp_camera_deinit();
        initCamera();
        stale = esp_camera_fb_get();
        if (stale) esp_camera_fb_return(stale);
        fb = esp_camera_fb_get();
    }
    if (!fb) {
        Serial.println("[CAM ERROR] Failed to grab frame buffer.");
        return false;
    }

    Serial.printf("[CAM] Frame captured: %u bytes (%dx%d) mode=%s\n",
                  fb->len, fb->width, fb->height, mode);

    HTTPClient http;
    http.begin(apiUrl("/predict"));

    String boundary = "----WebKitFormBoundaryHydroSyncESP32";
    http.addHeader("Content-Type", "multipart/form-data; boundary=" + boundary);

    // Build multipart body header
    String head = "--" + boundary + "\r\n";
    head += "Content-Disposition: form-data; name=\"device_id\"\r\n\r\n";
    head += String(DEVICE_ID) + "\r\n";
    head += "--" + boundary + "\r\n";
    head += "Content-Disposition: form-data; name=\"mode\"\r\n\r\n";
    head += String(mode) + "\r\n";
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

    Serial.printf("[CAM] Sending %u bytes to %s ...\n", totalLen, apiUrl("/predict").c_str());
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

// Returns true when the dashboard queued a CAPTURE, and fills `mode` with the
// mode the operator asked for ("test" = archive only, "real" = run the AI).
bool pollRemoteCaptureCommand(String& mode) {
    if (WiFi.status() != WL_CONNECTED) return false;

    HTTPClient http;
    http.begin(apiUrl("/api/cam_command"));
    int code = http.GET();
    bool capture = false;
    if (code == 200) {
        String payload = http.getString();
        StaticJsonDocument<256> doc;
        if (!deserializeJson(doc, payload)) {
            const char* cmd = doc["command"] | "";
            if (strcmp(cmd, "CAPTURE") == 0) {
                mode = String((const char*)(doc["mode"] | "real"));
                Serial.printf("[REMOTE DASHBOARD] CAPTURE received (mode=%s)\n", mode.c_str());
                capture = true;
            }
        }
    }
    http.end();
    return capture;
}

// One round of work, then the radio is powered down. Nothing polls between
// rounds — that 1.5 s command poll was what kept the board hot.
void runCaptureRound() {
    WiFi.mode(WIFI_STA);
    connectWiFi();
    esp_wifi_set_ps(WIFI_PS_MIN_MODEM);

    // The camera is powered down between rounds. Left initialised, its DMA runs
    // free whenever nothing consumes frames — the 15 s idle wait between rounds
    // floods both frame buffers and fills the log with "cam_hal: FB-OVF" while
    // doing no useful work. That is what kept the board hot with the radio off.
    if (!initCamera()) {
        WiFi.disconnect(true);
        WiFi.mode(WIFI_OFF);
        Serial.println("[CAM] No camera this round, radio off.");
        return;
    }

    String mode = "real";
    bool shouldCapture = pollRemoteCaptureCommand(mode);

    if (millis() - lastAutoCaptureTime >= (unsigned long)CAPTURE_INTERVAL_S * 1000UL) {
        lastAutoCaptureTime = millis();
        shouldCapture = true;
    }

    if (shouldCapture) {
        captureAndUpload(mode.c_str());
    } else {
        Serial.println("[CAM] No command queued, nothing to upload.");
    }

    // Stop the sensor before the idle wait, or its DMA keeps filling buffers
    // for the next SLEEP_INTERVAL_S seconds (cam_hal: FB-OVF).
    esp_camera_deinit();

    WiFi.disconnect(true);
    WiFi.mode(WIFI_OFF);
    Serial.println("[CAM] Radio and camera off.");
}

void handleSerialCommands() {
    if (Serial.available() > 0) {
        String raw = Serial.readStringUntil('\n');
        raw.trim();

        // SET carries the rest of the line verbatim — an SSID or password is
        // case-sensitive, so it must never go through toUpperCase().
        String input = raw;
        input.toUpperCase();

        if (input.startsWith("SET WIFI ")) {
            String rest = raw.substring(9);
            int sep = rest.indexOf(' ');
            if (sep < 1) {
                Serial.println("[NVS] Usage: SET WIFI <ssid> <password>");
                return;
            }
            prefs.begin("aegis", false);
            prefs.putString("ssid", rest.substring(0, sep));
            prefs.putString("pass", rest.substring(sep + 1));
            prefs.end();
            Serial.printf("[NVS] Wi-Fi saved (%s). Rebooting...\n", rest.substring(0, sep).c_str());
            delay(300);
            ESP.restart();
        } else if (input.startsWith("SET SSID ")) {
            // The whole rest of the line is the SSID: phone hotspots are
            // commonly named "Samsung S30 Ultra", and SET WIFI would split on
            // the first space and store "Samsung" as the network name.
            String ssid = raw.substring(9);
            if (ssid.length() == 0) {
                Serial.println("[NVS] Usage: SET SSID <network name, spaces allowed>");
                return;
            }
            prefs.begin("aegis", false);
            prefs.putString("ssid", ssid);
            prefs.end();
            Serial.printf("[NVS] SSID saved (%s). Rebooting...\n", ssid.c_str());
            delay(300);
            ESP.restart();
        } else if (input.startsWith("SET PASS ")) {
            // Same reason as SET SSID: a password may contain spaces.
            String pass = raw.substring(9);
            if (pass.length() == 0) {
                Serial.println("[NVS] Usage: SET PASS <password, spaces allowed>");
                return;
            }
            prefs.begin("aegis", false);
            prefs.putString("pass", pass);
            prefs.end();
            Serial.printf("[NVS] Password saved (%u chars). Rebooting...\n", pass.length());
            delay(300);
            ESP.restart();
        } else if (input.startsWith("SET SERVER ")) {
            // Usage: SET SERVER <host> [port]  — the port defaults to SERVER_PORT.
            String rest = raw.substring(11);
            int sep = rest.indexOf(' ');
            String host = (sep < 0) ? rest : rest.substring(0, sep);
            String port = (sep < 0) ? String(SERVER_PORT) : rest.substring(sep + 1);
            if (host.length() == 0 || port.length() == 0) {
                Serial.println("[NVS] Usage: SET SERVER <ip> [port]");
                return;
            }
            prefs.begin("aegis", false);
            prefs.putString("host", host);
            prefs.putString("port", port);
            prefs.end();
            Serial.printf("[NVS] Server set to %s:%s. Rebooting...\n", host.c_str(), port.c_str());
            delay(300);
            ESP.restart();
        } else if (input == "SHOW") {
            Serial.printf("[CFG] SSID: %s | SERVER: %s:%s\n",
                          cfgSsid.c_str(), cfgHost.c_str(), cfgPort.c_str());
        } else if (input == "RESET") {
            prefs.begin("aegis", false);
            prefs.clear();
            prefs.end();
            Serial.println("[NVS] Cleared, back to config.h defaults. Rebooting...");
            delay(300);
            ESP.restart();
        } else if (input == "CAPTURE" || input == "SNAP" || input == "PHOTO") {
            Serial.println("[SERIAL] Manual capture round triggered (real mode)!");
            runCaptureRound();
        } else {
            Serial.println("\nCommands: CAPTURE | SET SSID <name> | SET PASS <password>  (spaces OK)");
            Serial.println("          SET WIFI <ssid> <password> | SET SERVER <ip> [port] | SHOW | RESET");
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

    // The camera is initialised inside runCaptureRound(), not here: it must be
    // down while the board idles, or its DMA floods the frame buffers.
    loadRuntimeConfig();

    // First round happens immediately so a freshly powered board reports in.
    lastAutoCaptureTime = millis() - (unsigned long)CAPTURE_INTERVAL_S * 1000UL;
    lastRoundTime = millis() - (unsigned long)SLEEP_INTERVAL_S * 1000UL;
}

void loop() {
    handleSerialCommands();

    if (millis() - lastRoundTime >= (unsigned long)SLEEP_INTERVAL_S * 1000UL) {
        runCaptureRound();
        lastRoundTime = millis();

#if CAM_SLEEP_ENABLED
        // Light sleep, not deep sleep: the USB CDC port stays enumerated so
        // SET WIFI / SET SERVER over Serial still works, and RAM is preserved
        // (deep sleep would restart setup() every wake). millis() is corrected
        // across the sleep, so the round timer does not drift.
        Serial.printf("[CAM] Sleeping %d s...\n", SLEEP_INTERVAL_S);
        Serial.flush();
        esp_sleep_enable_timer_wakeup((uint64_t)SLEEP_INTERVAL_S * 1000000ULL);
        esp_light_sleep_start();
        lastRoundTime = millis();
        Serial.println("[CAM] Awake.");
#endif
    }

    // Yield CPU time so cores don't spin at 100% duty cycle (drastically cools the board)
    delay(30);
}
