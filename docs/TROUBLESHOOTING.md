# DiscoBall Troubleshooting

## Quick health commands

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
docker logs --tail=150 discoball
curl -fsS http://127.0.0.1:${DISCOBALL_WEB_PORT:-8000}/healthz
```

## Container is running but connection resets

Check UI variables:

```bash
docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' discoball | grep -E '^UI_ENABLED=|^UI_PORT='
```

Expected:

```text
UI_ENABLED=1
UI_PORT=8000
```

If `UI_ENABLED` is missing or `0`, recreate the container with `UI_ENABLED=1`.

## ZimaOS paths

ZimaOS Files may show `/ZimaOS-HD/Media/...`, while SSH/Docker host paths are normally `/DATA/Media/...`.