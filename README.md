# Disco Ball
Docker-friendly post-transcode tagger/renamer.

## Naming schema (library root)
Example:
Half Baked (1998) [Comedy] {DVD}

- Title + Year from metadata (OMDb preferred)
- [Genre] = primary genre (first OMDb genre)
- {Source} defaults to DVD on your system

Output example:
/output/Half Baked (1998) [Comedy] {DVD}/Half Baked (1998) [Comedy] {DVD}.mp4
## Required setup: OMDb API key (for auto-naming)
DiscoBall uses OMDb to automatically fetch **Title / Year / Genre** so your output folder matches the schema:

`Title (Year) [Genre] {DVD}`

For security, the OMDb key is **not stored** in this repository or in `docker-compose.yml`.

### Add the key in ZimaOS Docker settings
In the ZimaOS Docker UI, open the **discoball** container and add an Environment Variable:

- `OMDB_API_KEY` = `<your OMDb key>`

Then **restart** the container.

> If `OMDB_API_KEY` is not set, DiscoBall will fall back to using the filename as the title guess and may not apply Year/Genre reliably.
### DVD-only note
This system is DVD-only, so `{DVD}` is applied via `SOURCE_TAG_DEFAULT=DVD` in the compose configuration.
