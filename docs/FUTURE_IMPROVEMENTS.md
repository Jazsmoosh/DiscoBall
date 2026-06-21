# Future Improvements

## Runtime-length sanity check

Add an optional runtime sanity check to reduce bad title selection from multi-title DVD rips.

Problem observed:

- Some DVDs produce multiple large MKV files.
- The largest file is not always the actual movie.
- A title-matched file with runtime close to the known movie runtime can be a better candidate than the largest file.

Proposed behavior:

1. Use OMDb metadata to retrieve known movie runtime when available.
2. Use `ffprobe` or equivalent media probing to measure candidate file runtime.
3. Penalize candidates outside a tolerance window, for example greater than 10 to 15 minutes or 12 percent away from known runtime.
4. Prefer title/year matched candidates whose runtime closely matches metadata.
5. Keep uncertain candidates in `_Unmatched` rather than selecting a likely wrong file.
6. Show runtime comparison in the web UI and JSON sidecar.

This should be configurable because bonus cuts, special editions, PAL speedup, and director cuts can differ from the theatrical runtime.