# DiscoBall Workflow Guide

## Core idea

DiscoBall works best when the incoming file lives inside a folder named like the movie:

```text
/watch/Movie Title (Year)/generic_makemkv_name.mkv
```

The file name can be generic. The folder should not be.

## MakeMKV -> HandBrake -> DiscoBall

```text
MakeMKV raw output      /DATA/Media/MakeMKV/output
HandBrake watch         /DATA/Media/MakeMKV/output
HandBrake output        /DATA/Media/HandBrake/output
DiscoBall watch         /DATA/Media/HandBrake/output
DiscoBall library       /DATA/Media/Library
```

Do not point DiscoBall at the MakeMKV raw output folder when HandBrake is part of the workflow.

## DVD multi-title behavior

Some DVDs create many MKV files: main movie, extras, commentary, trailers, menu artifacts, and alternate cuts. Do not merge every MakeMKV output file. Prefer the title-matched full-length movie candidate.