# Useful AI Agent & Creator Utilities

A collection of practical automations and tools.

## Authorized YouTube → Adobe MP4 (720p)

A GitHub Actions workflow that prepares videos you own or are explicitly allowed to download as Adobe-friendly MP4 files.

**Output:** H.264/AVC video + AAC audio in an MP4 container, at a maximum of 1280×720 landscape or 720×1280 portrait. Lower-resolution sources are not upscaled.

### Run it

1. Open **Actions → Download authorized video for Adobe → Run workflow**.
2. Paste the YouTube URL. The link supplied for this setup is prefilled.
3. Tick the rights-confirmation checkbox.
4. Run the workflow.
5. When complete, download the **adobe-720p-mp4** artifact from the run. GitHub provides it as a ZIP containing the MP4.

Artifacts are retained for 2 days.

### Rights and access

Use only videos you uploaded or have explicit permission to download and edit. The workflow does not bypass DRM, sign-in, paywalls, age gates, or other access controls. It accepts standard YouTube and youtu.be URLs only.

For videos you uploaded, YouTube Studio → Content → video menu → Download is the official MP4 route. YouTube states creator uploads can be downloaded as MP4 in 720p or 360p, depending on the source. YouTube Premium offline downloads are for playback inside YouTube, not transferable MP4 files for Premiere Pro.

### Run locally

Install FFmpeg and Python 3.10+, then:

```bash
python -m pip install -r requirements.txt
python scripts/download_for_adobe.py "https://youtu.be/VIDEO_ID"
```

The output is `output/adobe_720p.mp4`.
