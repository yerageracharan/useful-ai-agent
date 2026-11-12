#!/usr/bin/env python3
"""Download an authorized YouTube source and transcode it for Adobe NLEs."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

ALLOWED_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "www.youtu.be"}


def validate_url(value: str) -> str:
    parsed = urlparse(value.strip())
    if parsed.scheme != "https" or (parsed.hostname or "").lower() not in ALLOWED_HOSTS:
        raise ValueError("Use a standard https://youtube.com or https://youtu.be URL.")
    return value.strip()


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, check=True, text=True, capture_output=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="YouTube URL for a video you own or are authorized to download")
    parser.add_argument("--output-dir", default="output", help="Directory for the final MP4")
    args = parser.parse_args()

    try:
        url = validate_url(args.url)
    except ValueError as exc:
        parser.error(str(exc))

    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = output_dir / "source_tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    template = str(temp_dir / "source.%(ext)s")

    print("Downloading the authorized source (maximum selected height: 720p)...", flush=True)
    download_cmd = [
        sys.executable, "-m", "yt_dlp",
        "--no-playlist", "--no-warnings", "--quiet", "--no-progress",
        "--format", "bv*[height<=720]+ba/b[height<=720]/best",
        "--merge-output-format", "mkv",
        "--output", template,
        "--print", "after_move:filepath",
        url,
    ]
    result = run(download_cmd)
    printed = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not printed:
        raise RuntimeError("yt-dlp completed but did not report the downloaded file path.")
    source = Path(printed[-1]).resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Downloaded source not found: {source}")

    final_mp4 = output_dir / "adobe_720p.mp4"
    print("Transcoding to H.264/AAC MP4 (720p maximum)...", flush=True)
    scale_filter = (
        "scale=w='if(gte(iw,ih),min(iw,1280),min(iw,720))':"
        "h='if(gte(iw,ih),min(ih,720),min(ih,1280))':"
        "force_original_aspect_ratio=decrease:force_divisible_by=2"
    )
    ffmpeg_cmd = [
        "ffmpeg", "-hide_banner", "-y", "-i", str(source),
        "-map", "0:v:0", "-map", "0:a?",
        "-vf", scale_filter,
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart", str(final_mp4),
    ]
    run(ffmpeg_cmd)

    probe = run([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,width,height",
        "-of", "default=noprint_wrappers=1", str(final_mp4),
    ])
    print("\nAdobe-ready output:")
    print(probe.stdout.strip())
    print(f"File: {final_mp4}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or str(exc)).strip()
        print(f"Command failed: {detail}", file=sys.stderr)
        raise SystemExit(exc.returncode or 1)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
