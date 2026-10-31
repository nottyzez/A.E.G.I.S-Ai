/**
 * HydroSync / A.E.G.I.S. AI - Presentation Engine
 * Shared 3D Digital Twin & Hardware State Controller
 * Version: 3.2.0
 */

// ─── 3D DIGITAL TWIN (THREE.JS PROCEDURAL KALE & FLUIDICS) ───────────────────
class HydroponicTwin3D {
    constructor(canvas, options = {}) {
        this.canvas = canvas;
        this.options = Object.assign({
            deficiency: 'Control',
            isWireframe: false,
            enableBubbles: true,
            onLoad: null
        }, options);

        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.plantGroup = null;
        this.leaves = [];
        this.tankGroup = null;
        this.fluidMesh = null;
        this.bubbles = null;
        this.bubbleCount = 60;
        this.clock = new THREE.Clock();
        this.isPumping = false;
        this.currentDeficiency = this.options.deficiency;

        // Palette presets for deficiencies
        this.PALETTES = {
            'Control': { base: 0x10b981, tip: 0x34d399, stem: 0x059669, vein: 0x6ee7b7, roughness: 0.35 },
            'healthy': { base: 0x10b981, tip: 0x34d399, stem: 0x059669, vein: 0x6ee7b7, roughness: 0.35 },
            '-N':      { base: 0xeab308, tip: 0xfef08a, stem: 0xca8a04, vein: 0xfef9c3, roughness: 0.5 },
            'nitrogen':{ base: 0xeab308, tip: 0xfef08a, stem: 0xca8a04, vein: 0xfef9c3, roughness: 0.5 },
            '-P':      { base: 0x4338ca, tip: 0x7c3aed, stem: 0x312e81, vein: 0xa78bfa, roughness: 0.4 },
            'phosphorus': { base: 0x4338ca, tip: 0x7c3aed, stem: 0x312e81, vein: 0xa78bfa, roughness: 0.4 },
            '-K':      { base: 0xb45309, tip: 0xd97706, stem: 0x78350f, vein: 0xfcd34d, roughness: 0.6 },
            'potassium':{ base: 0xb45309, tip: 0xd97706, stem: 0x78350f, vein: 0xfcd34d, roughness: 0.6 }
        };

        this.init();
    }

    init() {
        // Scene setup
        this.scene = new THREE.Scene();
        this.scene.fog = new THREE.FogExp2(0x060a08, 0.04);

        // Camera setup
        const w = this.canvas.clientWidth || window.innerWidth;
        const h = this.canvas.clientHeight || window.innerHeight;
        this.camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 100);
        this.camera.position.set(0, 3.2, 5.2);

        // Renderer setup
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            antialias: true,
            alpha: true,
            powerPreference: 'high-performance'
        });
        this.renderer.setSize(w, h);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;

        // Orbit Controls
        if (typeof THREE.OrbitControls !== 'undefined') {
            this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
            this.controls.enableDamping = true;
            this.controls.dampingFactor = 0.05;
            this.controls.maxPolarAngle = Math.PI / 2 + 0.05;
            this.controls.minDistance = 2.0;
            this.controls.maxDistance = 9.0;
            this.controls.target.set(0, 0.8, 0);
        }

        this.setupLights();
        this.buildHydroponicTank();
        this.buildProceduralKale();
        this.buildBubbles();

        window.addEventListener('resize', () => this.onResize());
        this.animate();

        if (this.options.onLoad) this.options.onLoad();
    }

    setupLights() {
        const ambient = new THREE.AmbientLight(0xffffff, 0.8);
        this.scene.add(ambient);

        // Grow Light (Top down warm-spectrum light)
        const growLight = new THREE.DirectionalLight(0xfff5ea, 1.4);
        growLight.position.set(2, 6, 3);
        growLight.castShadow = true;
        growLight.shadow.mapSize.width = 1024;
        growLight.shadow.mapSize.height = 1024;
        this.scene.add(growLight);

        // Ambient emerald rim light (Settigation signature glow)
        const rimLight = new THREE.PointLight(0x10b981, 2.5, 8);
        rimLight.position.set(-3, 2, -2);
        this.scene.add(rimLight);

        // Tank underwater cyan glow
        const tankGlow = new THREE.PointLight(0x06b6d4, 1.8, 4);
        tankGlow.position.set(0, -0.4, 0);
        this.scene.add(tankGlow);
    }

    buildHydroponicTank() {
        this.tankGroup = new THREE.Group();

        // 1. Acrylic Tank Outer Box
        const tankGeo = new THREE.BoxGeometry(2.6, 1.4, 2.6);
        const tankMat = new THREE.MeshPhysicalMaterial({
            color: 0x11221a,
            metalness: 0.1,
            roughness: 0.1,
            transmission: 0.85,
            thickness: 0.8,
            transparent: true,
            opacity: 0.55,
            wireframe: this.options.isWireframe
        });
        const tankMesh = new THREE.Mesh(tankGeo, tankMat);
        tankMesh.position.y = -0.5;
        this.tankGroup.add(tankMesh);

        // 2. Black Net Pot Lid
        const lidGeo = new THREE.CylinderGeometry(1.35, 1.35, 0.1, 32);
        const lidMat = new THREE.MeshStandardMaterial({
            color: 0x18241d,
            roughness: 0.5,
            metalness: 0.2,
            wireframe: this.options.isWireframe
        });
        const lidMesh = new THREE.Mesh(lidGeo, lidMat);
        lidMesh.position.y = 0.2;
        this.tankGroup.add(lidMesh);

        // Plant Hole Collar
        const holeGeo = new THREE.CylinderGeometry(0.5, 0.42, 0.22, 24);
        const holeMat = new THREE.MeshStandardMaterial({ color: 0x0d1510, roughness: 0.8 });
        const holeMesh = new THREE.Mesh(holeGeo, holeMat);
        holeMesh.position.y = 0.26;
        this.tankGroup.add(holeMesh);

        // 3. Nutrient Fluid
        const fluidGeo = new THREE.BoxGeometry(2.45, 1.0, 2.45, 16, 1, 16);
        const fluidMat = new THREE.MeshStandardMaterial({
            color: 0x059669,
            roughness: 0.2,
            metalness: 0.1,
            transparent: true,
            opacity: 0.72,
            wireframe: this.options.isWireframe
        });
        this.fluidMesh = new THREE.Mesh(fluidGeo, fluidMat);
        this.fluidMesh.position.y = -0.65;
        this.tankGroup.add(this.fluidMesh);

        this.scene.add(this.tankGroup);
    }

    buildProceduralKale() {
        this.plantGroup = new THREE.Group();
        this.leaves = [];

        const palette = this.PALETTES[this.currentDeficiency] || this.PALETTES['Control'];

        // Central Main Stem
        const stemCurve = new THREE.CatmullRomCurve3([
            new THREE.Vector3(0, 0.2, 0),
            new THREE.Vector3(0.02, 0.6, 0.01),
            new THREE.Vector3(-0.02, 1.1, -0.01),
            new THREE.Vector3(0, 1.5, 0)
        ]);
        const stemGeo = new THREE.TubeGeometry(stemCurve, 24, 0.07, 12, false);
        this.stemMat = new THREE.MeshStandardMaterial({
            color: palette.stem,
            roughness: 0.5,
            wireframe: this.options.isWireframe
        });
        const stemMesh = new THREE.Mesh(stemGeo, this.stemMat);
        this.plantGroup.add(stemMesh);

        // Create 8 Lush Curly Kale Leaves (Tiered Canopy)
        const leafConfigs = [
            { y: 0.5, rotY: 0.0, scale: 0.9, bend: 0.7 },
            { y: 0.55, rotY: 1.25, scale: 0.95, bend: 0.75 },
            { y: 0.6, rotY: 2.5, scale: 0.9, bend: 0.7 },
            { y: 0.75, rotY: 3.75, scale: 1.1, bend: 0.65 },
            { y: 0.85, rotY: 5.0, scale: 1.15, bend: 0.6 },
            { y: 1.05, rotY: 0.6, scale: 1.0, bend: 0.5 },
            { y: 1.15, rotY: 2.1, scale: 0.85, bend: 0.45 },
            { y: 1.3, rotY: 4.2, scale: 0.65, bend: 0.35 }
        ];

        leafConfigs.forEach((cfg, idx) => {
            const leafMesh = this.createCurledLeaf(cfg.scale, cfg.bend, palette);
            leafMesh.position.set(0, cfg.y, 0);
            leafMesh.rotation.y = cfg.rotY;
            leafMesh.userData = { initialScale: cfg.scale, baseRotY: cfg.rotY, leafIndex: idx };
            this.leaves.push(leafMesh);
            this.plantGroup.add(leafMesh);
        });

        this.scene.add(this.plantGroup);
    }

    createCurledLeaf(scale, bend, palette) {
        const leafGroup = new THREE.Group();

        // Leaf Blade Curved Shape
        const shape = new THREE.Shape();
        shape.moveTo(0, 0);
        shape.bezierCurveTo(0.18, 0.3, 0.45, 0.7, 0.4, 1.4);
        shape.bezierCurveTo(0.35, 1.8, 0.15, 2.1, 0, 2.3);
        shape.bezierCurveTo(-0.15, 2.1, -0.35, 1.8, -0.4, 1.4);
        shape.bezierCurveTo(-0.45, 0.7, -0.18, 0.3, 0, 0);

        const geom = new THREE.ShapeGeometry(shape, 18);
        const pos = geom.attributes.position;
        // Apply ruffled kale curling along borders
        for (let i = 0; i < pos.count; i++) {
            const x = pos.getX(i);
            const y = pos.getY(i);
            const edgeDist = Math.abs(x);
            // Curl downwards and create ripples
            const zCurve = -Math.pow(y / 2.3, 1.8) * (bend * 0.8) + Math.sin(x * 12 + y * 6) * 0.05 * (edgeDist + 0.2);
            pos.setZ(i, zCurve);
        }
        geom.computeVertexNormals();

        const mat = new THREE.MeshStandardMaterial({
            color: palette.base,
            roughness: palette.roughness,
            metalness: 0.05,
            side: THREE.DoubleSide,
            wireframe: this.options.isWireframe
        });

        const mesh = new THREE.Mesh(geom, mat);
        mesh.rotation.x = Math.PI / 2 - bend;
        mesh.scale.set(scale, scale, scale);
        mesh.castShadow = true;
        mesh.receiveShadow = true;
        leafGroup.add(mesh);

        return leafGroup;
    }

    buildBubbles() {
        if (!this.options.enableBubbles) return;
        const bubbleGeo = new THREE.DodecahedronGeometry(0.04, 1);
        const bubbleMat = new THREE.MeshStandardMaterial({
            color: 0x67e8f9,
            roughness: 0.1,
            metalness: 0.2,
            transmission: 0.9,
            transparent: true,
            opacity: 0.6
        });

        this.bubbles = new THREE.InstancedMesh(bubbleGeo, bubbleMat, this.bubbleCount);
        const dummy = new THREE.Object3D();
        this.bubbleData = [];

        for (let i = 0; i < this.bubbleCount; i++) {
            const x = (Math.random() - 0.5) * 2.0;
            const y = -1.1 + Math.random() * 0.9;
            const z = (Math.random() - 0.5) * 2.0;
            const speed = 0.4 + Math.random() * 0.8;
            this.bubbleData.push({ x, y, z, speed, initialY: y });

            dummy.position.set(x, y, z);
            dummy.scale.setScalar(0.6 + Math.random() * 0.8);
            dummy.updateMatrix();
            this.bubbles.setMatrixAt(i, dummy.matrix);
        }
        this.bubbles.instanceMatrix.needsUpdate = true;
        this.tankGroup.add(this.bubbles);
    }

    setDeficiency(defClass) {
        this.currentDeficiency = defClass;
        const palette = this.PALETTES[defClass] || this.PALETTES['Control'];

        // Animate color transition smoothly
        if (typeof gsap !== 'undefined') {
            const targetColor = new THREE.Color(palette.base);
            const targetStem = new THREE.Color(palette.stem);

            this.leaves.forEach(leafGroup => {
                const mesh = leafGroup.children[0];
                if (mesh && mesh.material) {
                    gsap.to(mesh.material.color, {
                        r: targetColor.r,
                        g: targetColor.g,
                        b: targetColor.b,
                        duration: 0.8
                    });
                    mesh.material.roughness = palette.roughness;
                }
            });

            if (this.stemMat) {
                gsap.to(this.stemMat.color, {
                    r: targetStem.r,
                    g: targetStem.g,
                    b: targetStem.b,
                    duration: 0.8
                });
            }
        } else {
            this.leaves.forEach(leafGroup => {
                const mesh = leafGroup.children[0];
                if (mesh && mesh.material) {
                    mesh.material.color.setHex(palette.base);
                    mesh.material.roughness = palette.roughness;
                }
            });
            if (this.stemMat) this.stemMat.color.setHex(palette.stem);
        }
    }

    setWireframe(enabled) {
        this.options.isWireframe = enabled;
        this.scene.traverse(obj => {
            if (obj.isMesh && obj.material) {
                obj.material.wireframe = enabled;
            }
        });
    }

    setCameraView(viewName) {
        if (!this.camera || !this.controls) return;
        const targets = {
            'topdown': { pos: [0, 5.8, 0.05], look: [0, 0.8, 0] },
            'tank': { pos: [0, -0.2, 4.2], look: [0, -0.4, 0] },
            'isometric': { pos: [3.4, 2.8, 4.2], look: [0, 0.8, 0] },
            'front': { pos: [0, 1.5, 4.8], look: [0, 0.8, 0] }
        };

        const t = targets[viewName] || targets['isometric'];
        if (typeof gsap !== 'undefined') {
            gsap.to(this.camera.position, {
                x: t.pos[0],
                y: t.pos[1],
                z: t.pos[2],
                duration: 1.2,
                ease: 'power2.inOut'
            });
            gsap.to(this.controls.target, {
                x: t.look[0],
                y: t.look[1],
                z: t.look[2],
                duration: 1.2,
                ease: 'power2.inOut',
                onUpdate: () => this.controls.update()
            });
        } else {
            this.camera.position.set(t.pos[0], t.pos[1], t.pos[2]);
            this.controls.target.set(t.look[0], t.look[1], t.look[2]);
            this.controls.update();
        }
    }

    setPumping(active) {
        this.isPumping = active;
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        const dt = this.clock.getDelta();
        const time = this.clock.getElapsedTime();

        if (this.controls) this.controls.update();

        // 1. Plant Gentle Breathing sway
        if (this.plantGroup) {
            this.leaves.forEach((leaf, i) => {
                const sway = Math.sin(time * 1.5 + i * 0.8) * 0.02;
                leaf.rotation.z = sway;
            });
        }

        // 2. Liquid Undulation
        if (this.fluidMesh) {
            const pos = this.fluidMesh.geometry.attributes.position;
            const waveSpeed = this.isPumping ? 4.5 : 1.8;
            const waveAmp = this.isPumping ? 0.04 : 0.015;
            for (let i = 0; i < pos.count; i++) {
                const x = pos.getX(i);
                const z = pos.getZ(i);
                const y = Math.sin(x * 3.5 + time * waveSpeed) * Math.cos(z * 3.5 + time * waveSpeed) * waveAmp;
                pos.setY(i, y);
            }
            pos.needsUpdate = true;
        }

        // 3. Bubbles floating upward
        if (this.bubbles && this.bubbleData) {
            const dummy = new THREE.Object3D();
            const pumpSpeedMult = this.isPumping ? 2.8 : 1.0;
            for (let i = 0; i < this.bubbleCount; i++) {
                const b = this.bubbleData[i];
                b.y += b.speed * pumpSpeedMult * dt;
                if (b.y > -0.2) {
                    b.y = -1.1;
                    b.x = (Math.random() - 0.5) * 2.0;
                    b.z = (Math.random() - 0.5) * 2.0;
                }
                dummy.position.set(b.x, b.y, b.z);
                dummy.scale.setScalar(0.7 + Math.sin(time * 2 + i) * 0.2);
                dummy.updateMatrix();
                this.bubbles.setMatrixAt(i, dummy.matrix);
            }
            this.bubbles.instanceMatrix.needsUpdate = true;
        }

        this.renderer.render(this.scene, this.camera);
    }

    onResize() {
        if (!this.canvas || !this.renderer || !this.camera) return;
        const w = this.canvas.clientWidth || window.innerWidth;
        const h = this.canvas.clientHeight || window.innerHeight;
        this.camera.aspect = w / h;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(w, h);
    }
}


// ─── PRESENTATION STATE CONTROLLER ───────────────────────────────────────────
class PresentationStateController {
    constructor(callbacks = {}) {
        this.callbacks = Object.assign({
            onStatusUpdate: () => {},
            onLog: () => {},
            onModeChange: () => {},
            onPhaseChange: () => {}
        }, callbacks);

        this.mode = 'live'; // 'live' | 'demo'
        this.isShowcaseLocked = false;
        this.lockedClass = null;
        this.pollIntervalMs = 1000;
        this.pollTimer = null;
        this.isPollingBusy = false;

        // Current Hardware State Mirror
        this.state = {
            phase: 'STANDBY',
            phase_id: 0,
            ec: 1.85,
            ph: 6.20,
            temp: 26.5,
            last_update: new Date().toISOString(),
            dosing_plan: { pump1_ms: 0, pump2_ms: 0, pump3_ms: 0 },
            ratios: { r1_pct: 33.3, r2_pct: 33.3, r3_pct: 33.3 },
            volumes_ml: { pump1_ml: 0.0, pump2_ml: 0.0, pump3_ml: 0.0, total_volume_ml: 0.0 },
            deficiency_class: 'Control',
            stage: 'HEALTHY_NORMAL',
            confidence: 0.965,
            latest_image_url: '/static/latest_capture.jpg',
            calibration: {
                target_ec: 1.85,
                tank_volume_liters: 2.0,
                pump_flow_rate_ml_s: 1.20,
                priming_delay_s: 2.0
            }
        };

        // Firmware Relay Pinout Table
        this.RELAY_MAP = {
            1: { name: 'Inflow Diaphragm Pump', label: 'INFLOW', gpio: 5, role: 'sampling_in' },
            2: { name: 'Return Diaphragm Pump', label: 'RETURN', gpio: 6, role: 'sample_return' },
            3: { name: 'Rinse Diaphragm Pump', label: 'RINSE', gpio: 7, role: 'probe_rinse' },
            4: { name: 'Solenoid Drain Valve', label: 'DRAIN', gpio: 8, role: 'drain_waste' },
            5: { name: 'Peristaltic Pump 1 (N)', label: 'PUMP 1 (N)', gpio: 9, role: 'dose_n' },
            6: { name: 'Peristaltic Pump 2 (P)', label: 'PUMP 2 (P)', gpio: 10, role: 'dose_p' },
            7: { name: 'Peristaltic Pump 3 (K)', label: 'PUMP 3 (K)', gpio: 11, role: 'dose_k' }
        };

        // 6-Phase Physical Sequence
        this.PHASE_NAMES = [
            'STANDBY',
            'Sampling In (ดูดน้ำเข้า)',
            'Measuring & AI (วัดค่า & วิเคราะห์)',
            'Sample Return (วนน้ำกลับ)',
            'Dosing NPK (จ่ายปุ๋ย AI)',
            'Probe Rinse (ล้างหัววัด)',
            'Drain Waste (ระบายน้ำทิ้ง)'
        ];

        // Demo simulation counters
        this.demoPhaseTick = 0;
        this.demoCycleRunning = false;

        this.startPolling();
    }

    log(msg, type = 'info') {
        const timeStr = new Date().toLocaleTimeString();
        this.callbacks.onLog({ text: msg, type, timestamp: timeStr });
    }

    setMode(mode) {
        this.mode = mode;
        this.log(`🔄 สลับโหมดการทำงาน: ${mode === 'live' ? '🔴 Live Hardware' : '🧪 Demo Simulation'}`);
        this.callbacks.onModeChange(this.mode);
    }

    startPolling() {
        if (this.pollTimer) clearInterval(this.pollTimer);
        this.pollTimer = setInterval(() => this.tick(), this.pollIntervalMs);
        this.tick();
    }

    async tick() {
        if (this.mode === 'demo') {
            this.runDemoTick();
            return;
        }

        if (this.isPollingBusy) return;
        this.isPollingBusy = true;

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 1800);
            const res = await fetch('/api/status', { signal: controller.signal });
            clearTimeout(timeoutId);

            if (res.ok) {
                const data = await res.json();
                this.updateStateFromBackend(data);
            } else {
                this.log(`⚠️ ไม่สามารถติดต่อ Backend (/api/status status: ${res.status})`, 'warn');
            }
        } catch (err) {
            // Server offline or abort
            // Do not spam log, but allow smooth UI
        } finally {
            this.isPollingBusy = false;
        }
    }

    updateStateFromBackend(data) {
        // If showcase is locked, preserve showcase deficiency and dosing breakdown
        const lockedCls = this.isShowcaseLocked ? this.lockedClass : data.deficiency_class || this.state.deficiency_class;

        this.state = Object.assign({}, this.state, data, {
            deficiency_class: lockedCls
        });

        this.callbacks.onStatusUpdate(this.state);
        this.callbacks.onPhaseChange(this.state.phase_id, this.state.phase);
    }

    runDemoTick() {
        // Drift sensor metrics realistically
        this.state.ec = +(1.85 + (Math.sin(Date.now() / 3000) * 0.08)).toFixed(2);
        this.state.ph = +(6.20 + (Math.cos(Date.now() / 4000) * 0.06)).toFixed(2);
        this.state.temp = +(26.5 + (Math.sin(Date.now() / 6000) * 0.2)).toFixed(1);
        this.state.last_update = new Date().toISOString();

        if (this.demoCycleRunning) {
            this.demoPhaseTick++;
            if (this.demoPhaseTick >= 4) { // every 4 seconds step phase
                this.demoPhaseTick = 0;
                let nextPhaseId = this.state.phase_id + 1;
                if (nextPhaseId > 6) {
                    nextPhaseId = 0;
                    this.demoCycleRunning = false;
                    this.log('🏁 จบวงจร Full Automated AI Cycle (Demo Completed)');
                }
                this.state.phase_id = nextPhaseId;
                this.state.phase = this.PHASE_NAMES[nextPhaseId] || 'STANDBY';
                this.callbacks.onPhaseChange(this.state.phase_id, this.state.phase);
            }
        }

        this.callbacks.onStatusUpdate(this.state);
    }

    // ── Command Dispatches ───────────────────────────────────────────────────
    async sendRelayCommand(relayIndex, durationMs = 2000) {
        const relayInfo = this.RELAY_MAP[relayIndex] || { name: `Relay #${relayIndex}`, gpio: '?' };
        this.log(`⚡ สั่งงาน ${relayInfo.name} (GPIO ${relayInfo.gpio}) เป็นเวลา ${durationMs} ms...`);

        if (this.mode === 'demo') {
            this.log(`✅ [Demo] สั่งงาน Relay #${relayIndex} สำเร็จ`);
            return { status: 'ok', mode: 'demo' };
        }

        try {
            const res = await fetch('/api/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    command: 'MANUAL_RELAY',
                    relay: relayIndex,
                    duration_ms: durationMs
                })
            });
            const data = await res.json();
            this.log(`✅ สั่งงาน Relay #${relayIndex} เรียบร้อยแล้ว`);
            return data;
        } catch (err) {
            this.log(`❌ ส่งคำสั่ง Relay #${relayIndex} ล้มเหลว: ${err.message}`, 'error');
            throw err;
        }
    }

    async startCycle() {
        this.log('🚀 เริ่มต้นวงจร Full AI Cycle: ส่งคำสั่ง START_CYCLE ไปยัง ESP32...');
        if (this.mode === 'demo') {
            this.demoCycleRunning = true;
            this.demoPhaseTick = 0;
            this.state.phase_id = 1;
            this.state.phase = this.PHASE_NAMES[1];
            this.callbacks.onPhaseChange(1, this.state.phase);
            this.log('✅ [Demo] เริ่มต้น Phase 1 (Sampling In)');
            return { status: 'ok' };
        }

        try {
            const res = await fetch('/api/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: 'START_CYCLE' })
            });
            const data = await res.json();
            this.log('✅ ส่งคำสั่ง START_CYCLE สำเร็จ: ESP32 กำลังเริ่ม Phase 1');
            return data;
        } catch (err) {
            this.log(`❌ ส่งคำสั่ง START_CYCLE ล้มเหลว: ${err.message}`, 'error');
            throw err;
        }
    }

    async emergencyStop() {
        this.log('🛑 EMERGENCY STOP: สั่งปิดปั๊มและวาล์วทุกตัวทันที!', 'error');
        if (this.mode === 'demo') {
            this.demoCycleRunning = false;
            this.state.phase_id = 0;
            this.state.phase = 'STANDBY';
            this.callbacks.onPhaseChange(0, 'STANDBY');
            this.log('🔒 [Demo] ระบบฮาร์ดแวร์จำลองตัดการทำงานเรียบร้อย');
            return { status: 'ok' };
        }

        try {
            const res = await fetch('/api/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: 'STOP' })
            });
            this.log('🔒 สัญญาณตัดฮาร์ดแวร์ถูกส่งไปยัง ESP32 แล้ว');
            return await res.json();
        } catch (err) {
            this.log(`❌ Emergency Stop ล้มเหลว: ${err.message}`, 'error');
            throw err;
        }
    }

    async triggerCameraCapture() {
        this.log('📸 สั่งการ ESP32-CAM บันทึกภาพมุมสูง (QUEUED CAPTURE)...');
        if (this.mode === 'demo') {
            this.log('✅ [Demo] ถ่ายภาพจำลองสำเร็จ');
            return { status: 'ok' };
        }

        try {
            const res = await fetch('/api/cam_command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: 'CAPTURE' })
            });
            this.log('✅ สั่งถ่ายภาพสำเร็จ ESP32-CAM กำลังดึงคำสั่ง...');
            return await res.json();
        } catch (err) {
            this.log(`❌ ส่งคำสั่งถ่ายภาพล้มเหลว: ${err.message}`, 'error');
            throw err;
        }
    }

    // ── Showcase Lock ────────────────────────────────────────────────────────
    lockShowcase(symptomClass) {
        this.isShowcaseLocked = true;
        this.lockedClass = symptomClass;
        this.state.deficiency_class = symptomClass;

        const presets = {
            'Control': { p1: 0, p2: 0, p3: 0, stage: 'HEALTHY_NORMAL', conf: 0.985 },
            '-N': { p1: 15000, p2: 0, p3: 0, stage: 'SYMPTOMATIC_DEFICIENCY_CONFIRMED', conf: 0.942 },
            '-P': { p1: 0, p2: 15000, p3: 0, stage: 'SYMPTOMATIC_DEFICIENCY_CONFIRMED', conf: 0.918 },
            '-K': { p1: 0, p2: 0, p3: 15000, stage: 'SYMPTOMATIC_DEFICIENCY_CONFIRMED', conf: 0.956 }
        };
        const p = presets[symptomClass] || presets['Control'];
        this.state.dosing_plan = { pump1_ms: p.p1, pump2_ms: p.p2, pump3_ms: p.p3 };
        this.state.stage = p.stage;
        this.state.confidence = p.conf;

        this.log(`🎯 ล็อกโหมดสาธิตอาการขาดธาตุอาหาร: [ ${symptomClass} ]`);
        this.callbacks.onStatusUpdate(this.state);
    }

    resumeLiveSync() {
        this.isShowcaseLocked = false;
        this.lockedClass = null;
        this.log('🔄 ปลดล็อกโหมดสาธิต: กลับสู่การซิงค์ข้อมูลฮาร์ดแวร์แบบ Real-time');
        this.tick();
    }
}
