# DiscoBall Workflow Guide

## Core idea

DiscoBall works best when the incoming file lives inside a folder named like the movie:

```text
/watch/Movie Title (Year)/generic_makemkv_name.mkv
```

The file name can be generic. The folder should not be.

## Good inputs

```text
/watch/Cast Away (2000)/F4_t00.mkv
/watch/Se7en (1995)/A1_t00.mkv
/watch/The Matrix (1999)/title_t00.mkv
```

## Bad inputs

```text
/watch/F4_t00.mkv
/watch/title_t00.mkv
/watch/output/A1_t00.mkv
```

These do not provide enough title context.

## Recommended rip/transcode protocol

1. Create a folder named `Movie Title (Year)` in the ingest/watch root.
2. Configure MakeMKV or your transcoder to output into that folder.
3. Let the rip/transcode finish.
4. DiscoBall waits for file-size stability.
5. DiscoBall identifies the movie.
6. DiscoBall moves/copies/hardlinks into the library output root.
7. DiscoBall writes a `.discoball.json` sidecar.

## What `_Unmatched` means

A file goes to `_Unmatched` when DiscoBall refuses to make a confident match. This is intentional. It is better to require manual review than to place the wrong movie into the library.

Common causes:

- folder does not contain a title/year hint
- OMDb key is missing or invalid
- title is ambiguous
- file is too small
- metadata confidence is below `MIN_CONFIDENCE`

## Direct identify check

Use this before processing a large batch:

```bash
docker compose run --rm discoball discoball identify "/watch/Se7en (1995)/A1_t00.mkv"
```

Expected:

- query uses `Se7en`
- year is `1995`
- match title is correct
- confidence is high

## Direct one-file process

```bash
docker compose run --rm discoball discoball once "/watch/Se7en (1995)/A1_t00.mkv"
```

## Watcher process

```bash
docker compose up -d
```

Follow logs:

```bash
docker compose logs -f discoball
```
