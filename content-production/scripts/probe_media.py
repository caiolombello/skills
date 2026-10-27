#!/usr/bin/env python3
"""Read selected metadata from one local media file; requires ffprobe, not FFmpeg rendering."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media", type=Path)
    args = parser.parse_args()
    media = args.media.expanduser().resolve()
    if not media.is_file():
        print(json.dumps({"error": "Expected an existing local media file"}), file=sys.stderr)
        return 2
    executable = shutil.which("ffprobe")
    if not executable:
        print(json.dumps({"error": "ffprobe unavailable; no installation attempted"}), file=sys.stderr)
        return 2
    entries = (
        "format=format_name,duration,size:"
        "stream=index,codec_type,codec_name,width,height,pix_fmt,"
        "sample_aspect_ratio,display_aspect_ratio,r_frame_rate,avg_frame_rate,"
        "sample_rate,channels,channel_layout,duration,nb_frames:"
        "stream_tags=rotate:stream_side_data=rotation"
    )
    try:
        result = subprocess.run(
            [executable, "-v", "error", "-protocol_whitelist", "file,pipe",
             "-show_entries", entries, "-of", "json", "-i", str(media)],
            text=True, capture_output=True, timeout=30, check=False,
        )
        if result.returncode:
            print(json.dumps({"error": "ffprobe failed", "details": result.stderr.strip()}), file=sys.stderr)
            return 2
        metadata = json.loads(result.stdout)
    except (OSError, subprocess.TimeoutExpired, ValueError) as error:
        print(json.dumps({"error": type(error).__name__, "details": str(error)}), file=sys.stderr)
        return 2
    print(json.dumps({
        "file": str(media),
        "format": metadata.get("format", {}),
        "streams": metadata.get("streams", []),
        "verification": "metadata only; playback, visual content, audio quality and delivery acceptance unverified",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
