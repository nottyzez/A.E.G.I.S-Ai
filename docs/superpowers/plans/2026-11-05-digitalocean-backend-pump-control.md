# DigitalOcean Cloud Backend & End-to-End Pump Control Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a production-ready DigitalOcean Cloud Backend and Electronic Control Cockpit pipeline that reliably queues, authenticates, dispatches, and acknowledges pump/relay commands from the Web Dashboard down to the physical ESP32-S3 7-relay controller and ESP32-CAM over the internet.

**Architecture:** We introduce `server/cloud_broker.py` (`CloudCommandBroker` with FIFO command queue, 15s TTL auto-expiration, priority emergency `STOP`, `POST /api/command/ack`, and device heartbeat tracking) and `server/state_store.py` (`StateStore` backed by SQLite `server/runtime_state.db` for restart-proof telemetry & status persistence). We synchronize `main.py`, `firmware/esp32_main/esp32_main.ino`, `firmware/esp32_cam/esp32_cam.ino`, and `server/static/index.html` with the 8-Phase Preservation FSM (`Phase 0`–`Phase 7`), add Cloud Link/ACK badges and Control Token support to the Electronic Control Cockpit, and provide a complete single-Droplet Docker + Nginx + 2GB Swap deployment bundle in `deploy/digitalocean/`.

**Tech Stack:** Python 3.12, FastAPI, SQLite3 (`sqlite3`), React 18 + Tailwind CSS (`server/static/index.html`), ESP32-S3 Arduino C++ (`HTTPClient`, `ArduinoJson`), Docker Compose, Nginx.

**Spec:** `docs/superpowers/specs/2026-11-05-digitalocean-backend-pump-control-design.md`

## Global Constraints

- **Crop Terminology:** All Thai plant copy must exclusively use **ผักบุ้ง (Water Spinach)**.
- **Minimum Font Size in Control View:** Never use `text-[10px]` or `text-[11px]` inside `ElectronicControlTabView` (`server/static/index.html`); minimum font size is `12px` (`text-xs`).
- **Pump Runtime Safety Ceiling:** Neither backend (`main.py`), frontend (`calcPumpMs`), nor firmware (`esp32_main.ino`) may schedule a pump runtime exceeding `30000 ms` (30 seconds).
- **Command TTL Fail-Safe:** Queued hardware commands must auto-expire after `15.0 seconds` (`DEFAULT_COMMAND_TTL_SEC = 15.0`) if the ESP32 does not poll them, preventing stale pump actuation after a Wi-Fi drop.
- **Single-Worker Cloud Constraint:** DigitalOcean deployment (`Dockerfile` / `docker-compose.digitalocean.yml`) must run Uvicorn with `--workers 1` so TensorFlow loads once in memory and `CloudCommandBroker` state stays unified.
- **No `fastapi.testclient.TestClient`:** Never import `TestClient` in unit tests (`httpx` incompatibility in `ai-env312`); call FastAPI endpoint functions directly or inspect source files.

## Review Focus

- **Rapid Multi-Button Presses on Dashboard:** Clicking `MANUAL_RELAY R1` followed immediately by `MANUAL_RELAY R5` must enqueue both commands in FIFO order and deliver them sequentially on consecutive `GET /api/command` polls instead of overwriting the first command.
- **Stale Pump Command After Wi-Fi Drop (TTL Expiration):** A command enqueued while ESP32 is offline must expire after `ttl_sec` (`15s`) so when ESP32 polls later, `GET /api/command` returns `"IDLE"` and logs `"COMMAND_EXPIRED"`.
- **Emergency `STOP` Queue Flush:** Sending `command="STOP"` (or `"CANCEL_OVERRIDE"`) while multiple pump commands are sitting in the FIFO queue must cancel all pending queued commands immediately and deliver `"STOP"` first.
- **Unauthorized Public Internet Command Rejection:** When `AEGIS_REQUIRE_AUTH=1` (or `broker.require_auth = True`), `POST /api/command` without a valid `X-Control-Token` / `control_token` must raise `HTTPException(status_code=401)`.
- **Server Restart State Survival:** Updating sensor telemetry (`ec`, `ph`, `temp`) and `command_log` via `StateStore` must persist to SQLite and restore cleanly into a fresh `StateStore` instance.

---

### Task 1: Cloud Command Broker, Auth Guard & SQLite State Store (`server/cloud_broker.py` & `server/state_store.py`)

**Files:**
- Create: `server/cloud_broker.py`
- Create: `server/state_store.py`
- Modify: `main.py:45-135`, `main.py:390-605`, `main.py:720-745`
- Test: `tests/test_digitalocean_cloud_backend.py`

**Interfaces:**
- Produces:
  - `server/cloud_broker.py`: `CloudCommandBroker(default_ttl_sec: float = 15.0, heartbeat_timeout_sec: float = 5.0)` with methods `enqueue_command(payload: dict, ttl_sec: float | None = None) -> dict`, `poll_next_command(device_id: str = "esp32-s3-demo-box-01", now_epoch: float | None = None) -> dict`, `ack_command(command_id: str, device_id: str, status: str = "ACKED", extra: dict | None = None) -> dict`, `record_heartbeat(device_id: str, rssi_dbm: int | None = None, now_epoch: float | None = None) -> None`, `get_link_status(now_epoch: float | None = None) -> dict`, `verify_control_token(token: str | None) -> bool`, `verify_device_key(api_key: str | None) -> bool`
  - `server/state_store.py`: `StateStore(db_path: Path)` with methods `save_status(status_dict: dict) -> None`, `load_status() -> dict | None`, `append_telemetry(record: dict) -> None`, `get_telemetry_history(limit: int = 50) -> list[dict]`
  - `main.py`: Updated `PHASE_LABELS` (`0..7`), `post_dashboard_command(payload: dict, request: Request = None)`, `get_pending_command(device_id: str = "esp32-s3-demo-box-01", wait_ms: int = 0)`, `post_command_ack(payload: dict)`, `get_telemetry_history(limit: int = 50)`

- [ ] **Step 1: Write the failing test in `tests/test_digitalocean_cloud_backend.py` (`TestCloudBrokerAndStateStore`)**

```python
import tempfile
import unittest
from pathlib import Path
from fastapi import HTTPException
import main


class TestCloudBrokerAndStateStore(unittest.TestCase):
    def setUp(self):
        main.reset_presentation_override_state()
        main.cloud_broker.reset()

    def test_eight_phase_labels_and_jump_phase_0_to_7(self):
        for p in range(0, 8):
            self.assertIn(p, main.PHASE_LABELS)
            res = main.post_dashboard_command({"command": "JUMP_PHASE", "phase_id": p, "duration_ms": 3000})
            self.assertEqual(res["queued_command"]["phase_id"], p)

    def test_fifo_queue_preserves_rapid_commands_and_supports_ack(self):
        r1 = main.post_dashboard_command({"command": "MANUAL_RELAY", "relay": 1, "duration_ms": 2000})
        r2 = main.post_dashboard_command({"command": "MANUAL_RELAY", "relay": 5, "duration_ms": 4000})
        cmd1_id = r1["queued_command"]["command_id"]
        cmd2_id = r2["queued_command"]["command_id"]
        self.assertNotEqual(cmd1_id, cmd2_id)

        polled1 = main.get_pending_command(device_id="esp32-s3-demo-box-01")
        self.assertEqual(polled1["command_id"], cmd1_id)
        self.assertEqual(polled1["relay"], 1)

        ack_res = main.post_command_ack({
            "command_id": cmd1_id,
            "device_id": "esp32-s3-demo-box-01",
            "status": "ACKED",
            "rssi_dbm": -58,
        })
        self.assertEqual(ack_res["status"], "ok")
        self.assertEqual(main.current_hardware_status["cloud_link"]["last_ack_command_id"], cmd1_id)

        polled2 = main.get_pending_command(device_id="esp32-s3-demo-box-01")
        self.assertEqual(polled2["command_id"], cmd2_id)
        self.assertEqual(polled2["relay"], 5)

        polled3 = main.get_pending_command(device_id="esp32-s3-demo-box-01")
        self.assertEqual(polled3["command"], "IDLE")

    def test_command_ttl_auto_expires_stale_pump_commands(self):
        queued = main.cloud_broker.enqueue_command(
            {"command": "MANUAL_DOSE", "relay": 5, "duration_ms": 5000},
            ttl_sec=10.0,
            now_epoch=1000.0,
        )
        self.assertEqual(queued["status"], "QUEUED")
        # Poll 16 seconds later -> must auto-expire and return IDLE
        polled = main.cloud_broker.poll_next_command("esp32-s3-demo-box-01", now_epoch=1016.0)
        self.assertEqual(polled["command"], "IDLE")
        self.assertEqual(polled.get("expired_count"), 1)

    def test_emergency_stop_flushes_pending_queue(self):
        main.post_dashboard_command({"command": "MANUAL_RELAY", "relay": 1, "duration_ms": 5000})
        main.post_dashboard_command({"command": "MANUAL_DOSE", "volumes_ml": {"A": 5.0, "B": 5.0, "C": 5.0}})
        stop_res = main.post_dashboard_command({"command": "STOP"})
        self.assertEqual(stop_res["queued_command"]["command"], "STOP")

        # Next poll must immediately return STOP, and subsequent poll must be IDLE
        first_poll = main.get_pending_command()
        self.assertEqual(first_poll["command"], "STOP")
        second_poll = main.get_pending_command()
        self.assertEqual(second_poll["command"], "IDLE")

    def test_auth_guard_rejects_unauthorized_when_enabled(self):
        main.cloud_broker.require_auth = True
        main.cloud_broker.control_token = "secret-pin-9999"
        try:
            with self.assertRaises(HTTPException) as ctx:
                main.post_dashboard_command({"command": "MANUAL_RELAY", "relay": 1})
            self.assertEqual(ctx.exception.status_code, 401)

            ok_res = main.post_dashboard_command({
                "command": "MANUAL_RELAY",
                "relay": 1,
                "control_token": "secret-pin-9999",
            })
            self.assertEqual(ok_res["status"], "ok")
        finally:
            main.cloud_broker.require_auth = False

    def test_sqlite_state_store_persists_status_and_telemetry(self):
        from server.state_store import StateStore
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "test_state.db"
            store1 = StateStore(db_file)
            store1.save_status({"ec": 1.92, "ph": 6.15, "temp": 25.8, "phase_id": 4})
            store1.append_telemetry({
                "device_id": "esp32-s3-demo-box-01",
                "ec": 1.92,
                "ph": 6.15,
                "temp": 25.8,
                "deficiency_class": "-N",
                "stage": "PRE_SYMPTOMATIC_EARLY_WARNING",
                "pump1_ms": 4200,
                "pump2_ms": 2500,
                "pump3_ms": 2500,
            })

            store2 = StateStore(db_file)
            loaded = store2.load_status()
            self.assertIsNotNone(loaded)
            self.assertAlmostEqual(loaded["ec"], 1.92)
            hist = store2.get_telemetry_history(limit=10)
            self.assertEqual(len(hist), 1)
            self.assertEqual(hist[0]["deficiency_class"], "-N")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_digitalocean_cloud_backend.py -v`
Expected: FAIL (`AttributeError: module 'main' has no attribute 'cloud_broker'`)

- [ ] **Step 3: Implement `server/cloud_broker.py`, `server/state_store.py`, and integrate into `main.py`**

Create `server/cloud_broker.py` with `CloudCommandBroker`, `server/state_store.py` with `StateStore`, and wire them into `main.py` (`PHASE_LABELS` `0..7`, `post_dashboard_command`, `get_pending_command`, `post_command_ack`, `get_telemetry_history`, and `current_hardware_status["cloud_link"]`).

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_digitalocean_cloud_backend.py tests/test_presentation_override.py -v`
Expected: PASS

---

### Task 2: ESP32-S3 Main & ESP32-CAM Cloud Firmware Upgrade (`firmware/esp32_main/` & `firmware/esp32_cam/`)

**Files:**
- Modify: `firmware/esp32_main/config.h:6-20`
- Modify: `firmware/esp32_main/esp32_main.ino:90-244`
- Modify: `firmware/esp32_cam/config.h:6-18`
- Modify: `firmware/esp32_cam/esp32_cam.ino:100-170`
- Test: `tests/test_digitalocean_cloud_backend.py` (`TestFirmwareCloudIntegration`)

**Interfaces:**
- Consumes: `/api/command`, `/api/command/ack`, `/api/sensor`, `/api/status`, `/api/cam_command`, `/predict`, header `X-Device-Api-Key`
- Produces:
  - `firmware/esp32_main/config.h`: Defines `DEVICE_API_KEY`, `URL_ACK_COMMAND`, and DigitalOcean host config macros.
  - `firmware/esp32_main/esp32_main.ino`: Sends `X-Device-Api-Key` header, parses `command_id`, calls `sendCommandAck(commandId, cmd)` after triggering relays, supports `JUMP_PHASE` cases `0..7`, and reports `rssi_dbm` in `reportStatusToServer()`.
  - `firmware/esp32_cam/config.h` & `esp32_cam.ino`: Sends `X-Device-Api-Key` header on `/api/cam_command` and `/predict`.

- [ ] **Step 1: Add `TestFirmwareCloudIntegration` to `tests/test_digitalocean_cloud_backend.py`**

```python
class TestFirmwareCloudIntegration(unittest.TestCase):
    def test_esp32_main_supports_cloud_api_key_ack_and_8_phases(self):
        cfg = Path("firmware/esp32_main/config.h").read_text(encoding="utf-8")
        ino = Path("firmware/esp32_main/esp32_main.ino").read_text(encoding="utf-8")
        self.assertIn("DEVICE_API_KEY", cfg)
        self.assertIn("URL_ACK_COMMAND", cfg)
        self.assertIn("/api/command/ack", cfg)
        self.assertIn("X-Device-Api-Key", ino)
        self.assertIn("sendCommandAck", ino)
        self.assertIn("command_id", ino)
        for case_idx in range(0, 8):
            self.assertIn(f"case {case_idx}:", ino)

    def test_esp32_cam_sends_device_api_key(self):
        cfg = Path("firmware/esp32_cam/config.h").read_text(encoding="utf-8")
        ino = Path("firmware/esp32_cam/esp32_cam.ino").read_text(encoding="utf-8")
        self.assertIn("DEVICE_API_KEY", cfg)
        self.assertIn("X-Device-Api-Key", ino)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_digitalocean_cloud_backend.py -v`
Expected: FAIL (`"DEVICE_API_KEY" not found in firmware/esp32_main/config.h`)

- [ ] **Step 3: Update `firmware/esp32_main/config.h`, `firmware/esp32_main/esp32_main.ino`, `firmware/esp32_cam/config.h`, and `firmware/esp32_cam/esp32_cam.ino`**

Add `DEVICE_API_KEY`, `URL_ACK_COMMAND`, `X-Device-Api-Key` header attachment, `sendCommandAck(const char* commandId, const char* cmdName)`, `rssi_dbm` reporting (`WiFi.RSSI()`), and 8-phase `JUMP_PHASE` switch cases (`case 0:` through `case 7:`).

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_digitalocean_cloud_backend.py tests/test_chamber_fsm_preservation.py -v`
Expected: PASS

---

### Task 3: Electronic Control Cockpit UI Overhaul + Cloud Link & ACK Telemetry (`server/static/index.html`)

**Files:**
- Modify: `server/static/index.html:3566-4630`
- Create: `tests/test_electronic_control_cockpit.py`

**Interfaces:**
- Consumes: `liveHwStatus.cloud_link`, `POST /api/command` (with `X-Control-Token` / `control_token`), `PHASE_LABELS` `0..7`
- Produces:
  - `InteractiveChamberSchematic({ relays, activePhase, onToggleRelay, onSelectPhase })` with clickable relay nodes (`data-schematic-relay="R1"`..`"R7"`) and `STANDBY_PRESERVED` indicator in Phase 7.
  - Cloud Link & Control Token Bar (`data-cloud-status-bar`) displaying `ESP32-MAIN: ONLINE / OFFLINE`, `Queue / Last ACK`, and `Control Token (PIN)` input saved in `localStorage.getItem('aegis_control_token')`.
  - Segmented Sub-Tab Workspace (`data-control-tab="pumps" | "vision" | "simulation" | "pinout"`) keeping `#settings-schedule`, `#settings-pumps`, `#settings-vision`, `#settings-simulation` mounted in DOM.
  - Per-pump flow calibration binding `calcPumpMs(mlVal, pumpKey)` + Quick Volume buttons (`data-quick-dose="0" | "2.5" | "5" | "10"`) + 2 functional relay groups (`Fluidic Chamber Relays (R1–R4)` and `Peristaltic Nutrient Pumps (R5–R7)`) + interactive `VisionPanel` (`selectedPreview`).

- [ ] **Step 1: Write the failing tests in `tests/test_electronic_control_cockpit.py`**

```python
import re
import unittest
from pathlib import Path

INDEX_HTML = Path("server/static/index.html")


class TestElectronicControlCockpitAndCloudUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX_HTML.read_text(encoding="utf-8")
        start = cls.html.index("function ElectronicControlTabView")
        end = cls.html.index("const navItems =", start)
        cls.ctrl_block = cls.html[start:end]

    def test_interactive_chamber_schematic_and_8_phases_present(self):
        self.assertIn("function InteractiveChamberSchematic", self.html)
        for r in range(1, 8):
            self.assertIn(f'data-schematic-relay="R{r}"', self.html)
        self.assertIn("STANDBY_PRESERVED", self.html)
        for label in ("Pre-Return", "Sample Inflow", "Settling & Measure", "Sample Return",
                      "Peristaltic Dosing", "Probe Rinse", "Drain Waste", "Probe Preservation Soak"):
            self.assertIn(label, self.ctrl_block)

    def test_cloud_link_status_bar_and_control_token_present(self):
        self.assertIn("data-cloud-status-bar", self.ctrl_block)
        self.assertIn("aegis_control_token", self.ctrl_block)
        self.assertIn("X-Control-Token", self.ctrl_block)
        self.assertIn("cloud_link", self.ctrl_block)

    def test_segmented_subtabs_and_per_pump_dosing(self):
        self.assertIn("controlSubTab", self.ctrl_block)
        for tab_id in ("pumps", "vision", "simulation", "pinout"):
            self.assertIn(f'data-control-tab="{tab_id}"', self.ctrl_block)
        self.assertRegex(
            self.ctrl_block,
            r"const\s+calcPumpMs\s*=\s*\(\s*mlVal\s*,\s*pumpKey\s*=\s*['\"]A['\"]\s*\)",
        )
        for qv in ("0", "2.5", "5", "10"):
            self.assertIn(f'data-quick-dose="{qv}"', self.ctrl_block)
        self.assertIn("Fluidic Chamber Relays (R1–R4)", self.ctrl_block)
        self.assertIn("Peristaltic Nutrient Pumps (R5–R7)", self.ctrl_block)

    def test_vision_studio_selected_preview(self):
        v_start = self.html.index("function VisionPanel")
        v_end = self.html.index("function ElectronicControlTabView", v_start)
        vision_block = self.html[v_start:v_end]
        self.assertIn("selectedPreview", vision_block)
        self.assertIn("setSelectedPreview", vision_block)

    def test_no_sub_12px_fonts_in_control_tab(self):
        sub_12 = re.findall(r"text-\[(?:10|11)px\]", self.ctrl_block)
        self.assertEqual(sub_12, [])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_electronic_control_cockpit.py -v`
Expected: FAIL (`"function InteractiveChamberSchematic" not found`)

- [ ] **Step 3: Implement `<InteractiveChamberSchematic />`, Cloud Link Status & Control Token Bar, 8-Phase Stepper, Segmented Sub-Tabs, Per-Pump Dosing, and `<VisionPanel />` in `server/static/index.html`**

Ensure all existing section IDs (`#settings-schedule`, `#settings-pumps`, `#settings-vision`, `#settings-simulation`) and required Thai/English copy remain mounted in the DOM.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest tests/test_electronic_control_cockpit.py tests/test_dashboard_overhaul.py tests/test_presentation_override.py -v`
Expected: PASS

---

### Task 4: DigitalOcean Droplet Deployment Bundle (`deploy/digitalocean/`)

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.digitalocean.yml`
- Create: `deploy/digitalocean/nginx.conf`
- Create: `deploy/digitalocean/.env.example`
- Create: `deploy/digitalocean/setup_droplet.sh`
- Create: `docs/digitalocean_deployment_guide.md`
- Test: `tests/test_digitalocean_cloud_backend.py` (`TestDigitalOceanDeploymentBundle`)

**Interfaces:**
- Consumes: `main.py`, `requirements.txt`, `server/runtime_state.db`
- Produces: Complete reproducible single-Droplet deployment stack with `--workers 1`, 2 GB swapfile provisioning, Nginx reverse proxy on port `80` (`client_max_body_size 10M`), and persistent volume mounts for `server/runtime_state.db`, `server/calibration.json`, and `test_captures/`.

- [ ] **Step 1: Add `TestDigitalOceanDeploymentBundle` to `tests/test_digitalocean_cloud_backend.py`**

```python
class TestDigitalOceanDeploymentBundle(unittest.TestCase):
    def test_dockerfile_and_compose_enforce_single_worker_and_volumes(self):
        dockerfile = Path("Dockerfile").read_text(encoding="utf-8")
        compose = Path("docker-compose.digitalocean.yml").read_text(encoding="utf-8")
        nginx = Path("deploy/digitalocean/nginx.conf").read_text(encoding="utf-8")
        setup_sh = Path("deploy/digitalocean/setup_droplet.sh").read_text(encoding="utf-8")

        self.assertIn("--workers", dockerfile)
        self.assertIn("1", dockerfile)
        self.assertIn("AEGIS_REQUIRE_AUTH", compose)
        self.assertIn("client_max_body_size 10M", nginx)
        self.assertIn("/api/command", nginx)
        self.assertIn("swapfile", setup_sh)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_digitalocean_cloud_backend.py -v`
Expected: FAIL (`FileNotFoundError: Dockerfile`)

- [ ] **Step 3: Create `Dockerfile`, `docker-compose.digitalocean.yml`, `deploy/digitalocean/nginx.conf`, `deploy/digitalocean/.env.example`, `deploy/digitalocean/setup_droplet.sh`, and `docs/digitalocean_deployment_guide.md`**

- [ ] **Step 4: Run full verification suite**

Run: `python -m unittest tests/test_digitalocean_cloud_backend.py tests/test_electronic_control_cockpit.py tests/test_dashboard_overhaul.py tests/test_presentation_override.py tests/test_chamber_fsm_preservation.py -v`
Expected: PASS (100% of unit tests pass)

Run: `python scripts/verify_figma_implementation.py`
Expected: `26/26 Passed (100.0%)`
