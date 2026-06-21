# ZimaOS Media Pipeline: MakeMKV to HandBrake to Discoball

This is the recommended out-of-box workflow for running Discoball with MakeMKV and HandBrake on ZimaOS.

The working pipeline is:

```text
Disc -> MakeMKV raw rip -> HandBrake completed encode -> Discoball organized library
```

Discoball should watch the folder where finished media lands. When HandBrake is used, Discoball should watch HandBrake output, not MakeMKV raw output.

## Recommended ZimaOS folder layout

Use this layout on the Docker host:

```text
/DATA/AppData/makemkv
/DATA/AppData/handbrake/config
/DATA/AppData/discoball

/DATA/Media/MakeMKV/output
/DATA/Media/HandBrake/output
/DATA/Media/Library
```

In the ZimaOS web UI, the same media area may appear as:

```text
/ZimaOS-HD/Media/MakeMKV/output
/ZimaOS-HD/Media/HandBrake/output
/ZimaOS-HD/Media/Library
```

Over SSH and in Docker volume mappings, use the real host path that exists on the host, usually:

```text
/DATA/Media/...
```

## MakeMKV

MakeMKV writes raw disc rips to:

```text
/DATA/Media/MakeMKV/output
```

Recommended mappings:

```text
/DATA/AppData/makemkv      -> /config
/DATA/Media                -> /storage
/DATA/Media/MakeMKV/output -> /output
```

MakeMKV web UI example:

```text
Host port 6220 -> container port 5800
```

The optical drive also needs to be passed through to the container. Common examples are:

```text
/dev/sr0
/dev/sg0
```

The exact `/dev/sgX` device can vary by host.

## HandBrake

HandBrake watches MakeMKV output and writes completed encodes to HandBrake output.

Recommended mappings:

```text
/DATA/AppData/handbrake/config -> /config
/DATA/Media                    -> /storage
/DATA/Media/MakeMKV/output     -> /watch
/DATA/Media/HandBrake/output   -> /output
```

Recommended environment variables:

```text
AUTOMATED_CONVERSION=1
AUTOMATED_CONVERSION_CHECK_INTERVAL=300
AUTOMATED_CONVERSION_FORMAT=mkv
AUTOMATED_CONVERSION_KEEP_SOURCE=1
AUTOMATED_CONVERSION_PRESET=General/Very Fast 1080p30
AUTOMATED_CONVERSION_SOURCE_STABLE_TIME=120
```

HandBrake web UI example:

```text
Host port 15800 -> container port 5800
```

## Discoball

Discoball watches completed HandBrake output and organizes into the final library.

Recommended mappings:

```text
/DATA/AppData/discoball      -> /config
/DATA/Media/HandBrake/output -> /watch
/DATA/Media/Library          -> /output
```

Discoball web UI example:

```text
Host port 18000 -> container port 8000
```

## Important rule

For the recommended automated workflow, use this:

```text
MakeMKV /output    -> HandBrake /watch
HandBrake /output  -> Discoball /watch
Discoball /output  -> Library
```

Do not point Discoball at MakeMKV raw output when HandBrake is part of the workflow.

This direct mode can work for users who want raw MKV organization only, but it is not the recommended path when HandBrake is installed:

```text
MakeMKV /output -> Discoball /watch
```

## DVD multi-title behavior

DVDs often rip into multiple MKV files. This is normal.

A disc can include:

```text
Main movie
Deleted scenes
Trailers
Bonus features
Commentary versions
Short title artifacts
Alternate cuts
```

Do not automatically merge every MakeMKV output file. That can create a bad movie file by joining unrelated extras, trailers, deleted scenes, and short clips.

For a movie disc, the main movie is usually the largest and longest title. A typical DVD movie is often several GB and roughly 80 to 120 minutes.

## Verification commands

Run these over SSH on the ZimaOS host.

Show running containers:

```bash
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
```

Verify MakeMKV mounts:

```bash
docker inspect -f '{{range .Mounts}}{{println .Source "->" .Destination}}{{end}}' makemkv
```

Expected important line:

```text
/DATA/Media/MakeMKV/output -> /output
```

Verify HandBrake mounts:

```bash
docker inspect -f '{{range .Mounts}}{{println .Source "->" .Destination}}{{end}}' handbrake
```

Expected important lines:

```text
/DATA/Media/MakeMKV/output -> /watch
/DATA/Media/HandBrake/output -> /output
```

Verify Discoball mounts:

```bash
docker inspect -f '{{range .Mounts}}{{println .Source "->" .Destination}}{{end}}' discoball
```

Expected important lines:

```text
/DATA/Media/HandBrake/output -> /watch
/DATA/Media/Library -> /output
```

## Troubleshooting

### Discoball sees files too early

Discoball should watch completed HandBrake output:

```text
/DATA/Media/HandBrake/output
```

not raw MakeMKV output:

```text
/DATA/Media/MakeMKV/output
```

### HandBrake does not start converting

Check logs:

```bash
docker logs -f handbrake
```

Confirm HandBrake has this mount:

```text
/DATA/Media/MakeMKV/output -> /watch
```

### MakeMKV rips many files

That is normal for many DVDs. Do not merge all files automatically. Stage or keep the main movie title and archive or ignore extras unless intentionally processing bonus content.
