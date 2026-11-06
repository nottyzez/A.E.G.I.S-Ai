#!/usr/bin/env bash
# One-shot provisioning for a fresh Ubuntu 22.04/24.04 DigitalOcean Droplet.
# Run as root from the repo root:  sudo bash deploy/digitalocean/setup_droplet.sh
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_DIR"

# ---------------------------------------------------------------------------
# 1. Swap — the TensorFlow model needs 1.2-1.5 GB at load. A 2 GB droplet
#    reaches that while apt and pip are also resident, so without swap the
#    first request OOM-kills the container.
# ---------------------------------------------------------------------------
if ! swapon --show | grep -q swapfile; then
    fallocate -l 2G /swapfile || dd if=/dev/zero of=/swapfile bs=1M count=2048
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' >> /etc/fstab
    echo "2 GB swapfile enabled"
else
    echo "swapfile already active"
fi

# ---------------------------------------------------------------------------
# 2. Docker
# ---------------------------------------------------------------------------
if ! command -v docker >/dev/null 2>&1; then
    apt-get update
    apt-get install -y ca-certificates curl
    curl -fsSL https://get.docker.com | sh
fi

# ---------------------------------------------------------------------------
# 3. Firewall — 80 for the dashboard/ESP32, 22 for ssh. The app port 8000 stays
#    closed; everything reaches it through Nginx.
# ---------------------------------------------------------------------------
if command -v ufw >/dev/null 2>&1; then
    ufw allow OpenSSH || true
    ufw allow 80/tcp || true
    ufw --force enable || true
fi

# ---------------------------------------------------------------------------
# 4. Runtime files and env — Docker would create *directories* for these bind
#    mounts if they were missing.
# ---------------------------------------------------------------------------
mkdir -p test_captures
touch server/runtime_state.db server/calibration.json

if [ ! -f deploy/digitalocean/.env ]; then
    cp deploy/digitalocean/.env.example deploy/digitalocean/.env
    chmod 600 deploy/digitalocean/.env
    # A generated token, because the template ships an empty one and auth fails
    # closed — an empty CONTROL_TOKEN means every pump button answers 401.
    sed -i "s|^CONTROL_TOKEN=.*|CONTROL_TOKEN=$(openssl rand -hex 24)|" deploy/digitalocean/.env
    echo "Created deploy/digitalocean/.env from the template."
    echo "Your dashboard token (paste it into the browser prompt):"
    grep '^CONTROL_TOKEN=' deploy/digitalocean/.env | cut -d= -f2-
fi

# ---------------------------------------------------------------------------
# 5. Build and start
# ---------------------------------------------------------------------------
docker compose -f docker-compose.digitalocean.yml up -d --build

echo
echo "A.E.G.I.S. is starting. TensorFlow takes ~60-90 s to load on first boot."
echo "  Dashboard : http://<droplet-ip>/dashboard"
echo "  Health    : http://<droplet-ip>/health"
echo "  Logs      : docker compose -f docker-compose.digitalocean.yml logs -f aegis"
