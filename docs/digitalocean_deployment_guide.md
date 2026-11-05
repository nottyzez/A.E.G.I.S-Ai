# DigitalOcean Deployment Guide

Deploys A.E.G.I.S. to a single DigitalOcean Droplet: Nginx on port 80 in front
of uvicorn running **one** worker, with the dashboard, the AI ensemble and the
ESP32 command link all on that machine.

This covers infrastructure only. The command queue, acknowledgement and auth
(`server/cloud_broker.py`) are a separate workstream — until they exist the app
behaves exactly as it does on a laptop, minus the LAN restriction.

---

## 0. Create the account

DigitalOcean has **no free tier** — a card or PayPal is required before a
Droplet can be created.

1. Go to <https://cloud.digitalocean.com/registrations/new> and sign up with
   email, Google or GitHub. GitHub is one click if the repo is already there.
2. Confirm the verification email, then log in to the control panel.
3. **Billing → Add Payment Method.** A debit/credit card is the usual route in
   Thailand; a card that blocks foreign online charges will fail here — use one
   that allows THB→USD transactions, or PayPal.
4. Optional: **Billing → Promo Code.** Any credit code has to be applied before
   the Droplet exists, not after.

> **The $200 GitHub Student credit ended on 31 July 2026.** DigitalOcean left
> the Student Developer Pack and that offer was withdrawn; any balance was
> voided on 1 August 2026. Blog posts still advertising it are stale — do not
> budget for it. New accounts get roughly **$5 for 90 days**.

**Cost control.** The 2 GB Droplet below is $12/month, billed hourly (~$0.018/h),
so a day of rehearsal plus the presentation is well under $1. **Destroy the
Droplet when the presentation is over** — stopping it still bills for the disk.
And do not leave a public Droplet running with the pumps attached (§7).

## 1. Pick a Droplet size

| Size | RAM | Price | Verdict |
|---|---|---|---|
| Basic / Regular | 1 GB | $6/mo | **Too small.** TensorFlow needs ~1 GB just to import. |
| Basic / Regular | 2 GB | $12/mo | Works, with the 2 GB swap the setup script adds. |
| Basic / Regular | 4 GB | $24/mo | Comfortable; no swap thrash during image uploads. |

Choose **Ubuntu 24.04 LTS**, region closest to the greenhouse, and add your SSH
key. Note the public IP once it boots.

> **Check for "Private-only" before anything else.** A Droplet created without
> public networking shows a `Private-only` badge and gets only a `10.x.x.x`
> address. The ESP32 cannot reach that, and neither can you from outside
> DigitalOcean — the failure looks exactly like a dead server. Fix it on the
> Overview page: **Add public outbound or inbound access → Public IPv4**, or
> the **Networking** tab. The Overview's Connection Details should then show a
> Public IPv4 such as `165.245.x.x`. That is the address §6 uses.

## 2. Get the code onto the Droplet

```bash
ssh root@<droplet-ip>
apt-get update && apt-get install -y git
git clone -b feature/dashboard-overhaul https://github.com/nottyzez/A.E.G.I.S-Ai.git aegis
cd aegis
```

The `-b` matters: the presentation work (runtime network config, CAM power
saving, the DigitalOcean bundle itself) is not on `main`.

If SSH is unavailable — no key was added at creation, or the key is not on this
machine — use **Web Console** on the Droplet's Overview page. It is a browser
terminal as root and needs nothing installed locally.

The repo's untracked work (the calibration changes, the current plan) does not
travel with `git clone`. If you have not committed yet, use `rsync` instead:

```bash
rsync -av --exclude ai-env312 --exclude .git --exclude node_modules \
      ./ root@<droplet-ip>:/root/aegis/
```

## 3. Provision and start

```bash
bash deploy/digitalocean/setup_droplet.sh
```

The script creates a 2 GB `/swapfile`, installs Docker, opens only ports 22 and
80 with `ufw`, pre-creates the bind-mount files, copies `.env.example` to
`.env`, and runs `docker compose up -d --build`.

First build takes 5–10 minutes (TensorFlow is ~600 MB to download).

## 4. Set the tokens

```bash
nano deploy/digitalocean/.env
docker compose -f docker-compose.digitalocean.yml up -d
```

`CONTROL_TOKEN` and `DEVICE_API_KEY` are placeholders. Nothing reads them yet —
they are consumed when the cloud broker lands. Change them before the URL goes
public regardless, so the value is not the template string when it starts being
enforced.

## 5. Verify

```bash
curl http://<droplet-ip>/health
curl -o /dev/null -w '%{http_code}\n' http://<droplet-ip>/dashboard
docker compose -f docker-compose.digitalocean.yml logs -f aegis
```

`/health` should answer within ~90 s of the container starting. Before that the
ensemble is still loading — a connection refused in the first minute is normal,
not a failure.

## 6. Point the ESP32 at the Droplet

No re-flash needed — both sketches read host and port from NVS. Over serial at
115200, **port 80** because the Droplet serves through Nginx:

```
SET SERVER <droplet-ip> 80
```

The board saves it and reboots. `SHOW` prints `SERVER: <ip>:80` — check that
line before walking away, because a wrong port fails as a connection error that
looks like the server is down.

Port 80 only applies to the Droplet. Back on the lab LAN or a hotspot with
`main.py` running directly, set it back:

```
SET SERVER 192.168.43.5 8000
```

## 7. What is exposed

- **Read-only:** the whole dashboard, sensor charts and AI results are public at
  `http://<droplet-ip>/dashboard`.
- **Write:** every pump button is reachable by anyone who can load the page
  until the auth guard from the cloud plan is implemented. Do not leave the
  Droplet running unattended with a public IP and pumps connected.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Container restarts every ~30 s | OOM during model load | Confirm swap: `swapon --show`; use a 4 GB Droplet |
| `502 Bad Gateway` | uvicorn not up yet | Wait for `/health`; check `logs aegis` |
| ESP32 gets timeouts | Nginx 504 on long-poll | `proxy_read_timeout` must exceed the firmware's `wait_ms` (65 s in `nginx.conf`) |
| ESP32 gets timeouts, and the Droplet is up | Board still dialing `:8000` | `SHOW` on serial; re-send `SET SERVER <ip> 80` |
| Uploads fail (413) | body too large | `client_max_body_size 10M` in `nginx.conf` |
| Calibration resets on redeploy | bind mount missing | `setup_droplet.sh` touches `server/calibration.json`; re-run it |

## Updating the deployment

```bash
git pull
docker compose -f docker-compose.digitalocean.yml up -d --build
```

`server/calibration.json`, `server/runtime_state.db` and `test_captures/` live
outside the image, so a rebuild keeps the measured flow rates.
