# DiscoBall

DiscoBall is a Docker-friendly post-process watcher for MakeMKV-style media workflows. It watches an ingest folder, waits for a completed video file to stop changing, identifies the movie with metadata providers such as OMDb, and moves or copies the finished file into a clean library structure.

> DiscoBall is not a ripper, decryptor, downloader, or media source. It only organizes local video files that already exist in a folder you provide.

## What it does

Input example:

```text
/watch/Cast Away (2000)/F4_t00.mkv
```

Output example:

```text
/output/Cast Away (2000) [Adventure] {DVD}/Cast Away (2000) [Adventure] {DVD}.mkv
```

MakeMKV often creates generic filenames such as `title_t00.mkv`, `F4_t00.mkv`, `A1_t00.mkv`, or `VTS_03_1.mkv`. DiscoBall treats those names as generic and uses the nearest meaningful parent folder, such as `Cast Away (2000)`, as the metadata hint.

## ZimaOS quick install

Use this when MakeMKV and HandBrake are already installed and HandBrake outputs completed encodes to `/DATA/Media/HandBrake/output`.

```bash
curl -fsSL https://raw.githubusercontent.com/Jazsmoosh/DiscoBall/main/scripts/install-zimaos-discoball.sh -o /tmp/install-zimaos-discoball.sh
chmod +x /tmp/install-zimaos-discoball.sh
sudo /tmp/install-zimaos-discoball.sh
```

The installer prompts for your OMDb API key before starting the container.

Default ZimaOS workflow:

```text
MakeMKV output:      /DATA/Media/MakeMKV/output
HandBrake watch:     /DATA/Media/MakeMKV/output
HandBrake output:    /DATA/Media/HandBrake/output
DiscoBall watch:     /DATA/Media/HandBrake/output
DiscoBall library:   /DATA/Media/Library
DiscoBall config:    /DATA/AppData/discoball
```

Default ZimaOS ports:

```text
MakeMKV:    http://<zima-host-ip>:6220
HandBrake:  http://<zima-host-ip>:15800
DiscoBall:  http://<zima-host-ip>:18000
```

Do not point DiscoBall at MakeMKV raw output when HandBrake is part of the workflow.

## Docker Compose quick start

```bash
git clone https://github.com/Jazsmoosh/DiscoBall.git
cd DiscoBall
cp .env.example .env
nano .env
```

At minimum, set:

```env
OMDB_API_KEY=your_omdb_key_here
```

Set host folders:

```env
DISCOBALL_WATCH_PATH=/srv/media/incoming
DISCOBALL_OUTPUT_PATH=/srv/media/library
DISCOBALL_CONFIG_PATH=/srv/discoball/config
DISCOBALL_WEB_PORT=8000
UI_ENABLED=1
UI_PORT=8000
```

Start:

```bash
docker compose up -d --build
```

Open:

```text
http://<docker-host-ip>:8000
```

## Direct Docker run

For direct Docker usage, always enable the UI when publishing port `8000`:

```bash
docker run -d \
  --name discoball \
  --restart unless-stopped \
  -p 18000:8000 \
  -e UI_ENABLED=1 \
  -e UI_PORT=8000 \
  -e OMDB_API_KEY="your_omdb_key_here" \
  -v /srv/media/incoming:/watch:rw \
  -v /srv/media/library:/output:rw \
  -v /srv/discoball/config:/config:rw \
  ghcr.io/jazsmoosh/discoball:latest \
  discoball watch
```

## Documentation

- [Install Guide](docs/INSTALL.md)
- [Configuration Reference](docs/CONFIGURATION.md)
- [Workflow Guide](docs/WORKFLOW.md)
- [ZimaOS Media Pipeline](docs/ZIMAOS_MEDIA_PIPELINE.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Future Improvements](docs/FUTURE_IMPROVEMENTS.md)

## Legal note

DiscoBall does not provide, decrypt, bypass, download, or distribute media. It is a local file organization tool. Users are responsible for ensuring they have the right to process any media files they place into the watch folder and for complying with local law.