#!/usr/bin/env bash
set -Eeuo pipefail

IMAGE="${DISCOBALL_IMAGE:-ghcr.io/jazsmoosh/discoball:latest}"
CONTAINER="${DISCOBALL_CONTAINER_NAME:-discoball}"

CONFIG_DIR="${DISCOBALL_CONFIG_PATH:-/DATA/AppData/discoball}"
WATCH_DIR="${DISCOBALL_WATCH_PATH:-/DATA/Media/HandBrake/output}"
OUTPUT_DIR="${DISCOBALL_OUTPUT_PATH:-/DATA/Media/Library}"
PORT="${DISCOBALL_WEB_PORT:-18000}"

get_host_ip() {
  ip route get 1.1.1.1 2>/dev/null | awk '{for(i=1;i<=NF;i++){if($i=="src"){print $(i+1); exit}}}' || true
}

HOST_IP="$(get_host_ip)"
[ -z "$HOST_IP" ] && HOST_IP="<zima-host-ip>"

echo "=== DiscoBall ZimaOS installer ==="
echo "This installs or replaces DiscoBall only."
echo "MakeMKV and HandBrake are not modified."
echo
echo "DiscoBall watch:   $WATCH_DIR"
echo "DiscoBall library: $OUTPUT_DIR"
echo "DiscoBall config:  $CONFIG_DIR"
echo

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker command not found."
  exit 1
fi

if [ -z "${OMDB_API_KEY:-}" ]; then
  while true; do
    read -r -p "Paste OMDb API key: " OMDB_API_KEY
    if [ -n "$OMDB_API_KEY" ]; then
      break
    fi
    echo "OMDb API key is required for normal metadata matching. Press Ctrl+C to cancel."
  done
else
  echo "Using OMDB_API_KEY from environment."
fi

mkdir -p "$CONFIG_DIR" "$WATCH_DIR" "$OUTPUT_DIR"

docker ps -a --format '{{.Names}}|{{.Image}}' \
  | awk -F'|' 'tolower($1) ~ /discoball/ || tolower($2) ~ /discoball/ || tolower($2) ~ /jazsmoosh/ {print $1}' \
  | sort -u \
  | while read -r c; do
      [ -n "$c" ] || continue
      echo "Removing DiscoBall container: $c"
      docker stop "$c" >/dev/null 2>&1 || true
      docker rm "$c" >/dev/null 2>&1 || true
    done

if ss -ltnp 2>/dev/null | grep -q ":${PORT}\b"; then
  echo "ERROR: Port $PORT is still occupied."
  ss -ltnp 2>/dev/null | grep ":${PORT}\b" || true
  exit 1
fi

docker pull "$IMAGE"

docker run -d \
  --name "$CONTAINER" \
  --restart unless-stopped \
  -p "${PORT}:8000" \
  -e WATCH_DIR="/watch" \
  -e OUTPUT_DIR="/output" \
  -e CONFIG_DIR="/config" \
  -e UI_ENABLED="1" \
  -e UI_PORT="8000" \
  -e STABLE_TIME_SECONDS="${STABLE_TIME_SECONDS:-120}" \
  -e CHECK_INTERVAL_SECONDS="${CHECK_INTERVAL_SECONDS:-30}" \
  -e VIDEO_EXTENSIONS="${VIDEO_EXTENSIONS:-mkv,mp4,m4v}" \
  -e LOG_LEVEL="${LOG_LEVEL:-INFO}" \
  -e PROVIDERS="${PROVIDERS:-omdb,imdb}" \
  -e OMDB_API_KEY="$OMDB_API_KEY" \
  -e IMDB_SQLITE_PATH="${IMDB_SQLITE_PATH:-/config/imdb.sqlite}" \
  -e MIN_CONFIDENCE="${MIN_CONFIDENCE:-0.64}" \
  -e MIN_VIDEO_SIZE_MB="${MIN_VIDEO_SIZE_MB:-50}" \
  -e INCLUDE_GENRE_TAG="${INCLUDE_GENRE_TAG:-1}" \
  -e INCLUDE_SOURCE_TAG="${INCLUDE_SOURCE_TAG:-1}" \
  -e SOURCE_TAG_DEFAULT="${SOURCE_TAG_DEFAULT:-DVD}" \
  -e MOVIE_ROOT_SUBDIR="${MOVIE_ROOT_SUBDIR:-}" \
  -e TV_ROOT_SUBDIR="${TV_ROOT_SUBDIR:-TV}" \
  -e UNMATCHED_SUBDIR="${UNMATCHED_SUBDIR:-_Unmatched}" \
  -e FILE_ACTION="${FILE_ACTION:-move}" \
  -e CONFLICT_POLICY="${CONFLICT_POLICY:-suffix}" \
  -e NAMING_STYLE="${NAMING_STYLE:-discoball}" \
  -e PREFER_PARENT_FOR_GENERIC="${PREFER_PARENT_FOR_GENERIC:-1}" \
  -v "$CONFIG_DIR:/config:rw" \
  -v "$WATCH_DIR:/watch:rw" \
  -v "$OUTPUT_DIR:/output:rw" \
  "$IMAGE" \
  discoball watch

ok=0
for i in $(seq 1 30); do
  if curl -fsS --max-time 3 "http://127.0.0.1:${PORT}/healthz" >/tmp/discoball-health.json 2>/tmp/discoball-curl.err; then
    ok=1
    echo "Health check succeeded on attempt $i."
    break
  fi
  sleep 2
done

docker ps --filter name="$CONTAINER" --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
docker logs --tail=80 "$CONTAINER" || true

echo
echo "DiscoBall URL: http://${HOST_IP}:${PORT}"

if [ "$ok" -ne 1 ]; then
  echo "WARNING: Health check did not return success during startup window."
  exit 2
fi