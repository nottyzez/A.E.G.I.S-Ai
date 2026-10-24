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
#define SERVER_PORT         8000
#define PREDICT_URL         "http://" SERVER_HOST ":8000/predict"
#define URL_POLL_CAM_COMMAND "http://" SERVER_HOST ":8000/api/cam_command"
#define DEVICE_ID           "esp32-s3-cam-topdown"

// Camera Capture Settings
#define JPEG_QUALITY        10       // 10-12: High clarity for ML Auto-Cropper
#define CAPTURE_INTERVAL_S  60       // Demo capture interval (60 seconds between auto-uploads)

#endif // CAM_CONFIG_EXAMPLE_H
