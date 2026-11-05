#ifndef CAM_CONFIG_EXAMPLE_H
#define CAM_CONFIG_EXAMPLE_H

#include <Arduino.h>

// ==============================================================================
// 1. Wi-Fi & Central Server Network Configuration (Template)
// ==============================================================================
// ให้คัดลอกไฟล์นี้เป็น config.h และกรอกข้อมูล Wi-Fi และ IP เซิร์ฟเวอร์จริง
#define WIFI_SSID           "YOUR_WIFI_SSID"
#define WIFI_PASSWORD       "YOUR_WIFI_PASSWORD"
#define SERVER_HOST         "192.168.1.100"      // IP ของคอมพิวเตอร์ที่รัน FastAPI main.py
#define SERVER_PORT         8000   // ค่า fallback: SET SERVER <host> <port> เขียนทับได้ทั้งคู่
#define DEVICE_ID           "esp32-s3-cam-topdown"

// URL /predict และ /api/cam_command ถูกสร้างตอนรัน (runtime) จาก SERVER_HOST
// ไม่ได้ hardcode ไว้แล้ว — ค่าด้านบนเป็นแค่ fallback เมื่อ NVS ว่าง
// ตั้งค่าผ่าน Serial 115200 ได้โดยไม่ต้องคอมไพล์ใหม่:
//   SET SSID <name>          (ทั้งบรรทัดที่เหลือ — ใส่ช่องว่างได้)
//   SET PASS <password>      (ทั้งบรรทัดที่เหลือ — ใส่ช่องว่างได้)
//   SET WIFI <ssid> <password>   (ทางลัดบรรทัดเดียว; ชื่อมีช่องว่างจะพัง)
//   SET SERVER <ip> [port]
//   SHOW
//   RESET        (ล้าง NVS กลับไปใช้ค่าในไฟล์นี้)

// Camera Capture Settings
#define JPEG_QUALITY        10       // 10-12: High clarity for ML Auto-Cropper
#define CAPTURE_INTERVAL_S  60       // Auto-capture every 60 s (a dashboard button can force one)

// Power / thermal. The radio is powered ON only during a capture round, then
// the board light-sleeps. Continuous polling kept the board hot.
#define SLEEP_INTERVAL_S    15       // Length of one sleep; a dashboard button waits at most this long
#define CAM_SLEEP_ENABLED   1        // 0 = never sleep, keep Wi-Fi on (old behaviour, runs hot)

#endif // CAM_CONFIG_EXAMPLE_H
