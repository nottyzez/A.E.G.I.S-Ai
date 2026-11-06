# LAN backup server

A second way to run A.E.G.I.S. when the Droplet is not reachable (no internet at
the venue, droplet down, or you just want the rig on the local hotspot). It is
**independent of `deploy/digitalocean/`** — nothing here is a copy of that
bundle and nothing there needs to change.

| | Droplet (`deploy/digitalocean/`) | This backup |
|---|---|---|
| Runs on | Ubuntu VM, Docker + Nginx | this laptop, plain Python |
| Address | `165.245.191.33:80` | `10.187.70.201:8000` |
| Control token | required (`AEGIS_REQUIRE_AUTH=1`) | none (`0`) |
| Survives the laptop sleeping | yes | no |

`10.187.70.201` is a DHCP lease from the `AEGIS` hotspot — confirm it with
`ipconfig` before every run; if it changed, the board needs a new `SET SERVER`.

## Start

```bat
deploy\lan-backup\start-backup.bat
```

It refuses to start when port 8000 is already taken, so a stale process cannot
masquerade as a fresh one. Logs land in `logs/backup-server.{out,err}.log`.

Use `python -m uvicorn main:app --host 0.0.0.0 --port 8000`, **not**
`python main.py` — the latter closes stderr right after the model loads on this
machine (`lost sys.stderr`) and the server dies before it binds.

## Point the rig at it

On both boards (serial 115200):

```
SET WIFI AEGIS <hotspot password>
SET SERVER 10.187.70.201 8000
SHOW
```

`SHOW` must print `10.187.70.201:8000`. To go back to the Droplet:

```
SET SERVER 165.245.191.33 80
```

The WiFi password lives in `firmware/*/config.h`, which is gitignored — do not
put it in this file.

## Stop

```bat
deploy\lan-backup\stop-backup.bat
```

## Check

```bat
curl http://10.187.70.201:8000/health
curl http://10.187.70.201:8000/api/command
```

Both must answer 200. Windows Firewall already has an allow rule for TCP 8000;
if another machine cannot reach it, that rule is what to check.
