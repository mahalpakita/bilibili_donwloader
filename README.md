# ✨ Bilibili Downloader ✨

A fast, easy-to-use downloader for Bilibili videos with a cute, modern GUI and CLI support.

## Features

- 🎬 **Download Bilibili videos** in high quality
- 📺 **GUI and CLI modes** for flexibility
- 🎵 **Audio-only option** to extract MP3 from videos
- 📊 **Real-time progress bar** with speed and ETA display
- ⚡ **Optimized for speed** with parallel fragment downloads
- 🎨 **Modern, cute design** with custom color scheme

## Requirements

- Python 3.7+
- yt-dlp
- FFmpeg (for video merging and audio conversion)

## Installation

### 1. Install Python packages

```bash
pip install yt-dlp
```

### 2. Install FFmpeg

**Windows:**
- Using Chocolatey: `choco install ffmpeg.`
- Or download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH


Then:
1. Paste your Bilibili video URL
2. Choose output folder
3. Optionally select "Audio Only" for MP3 extraction
4. Click "⬇️ Download Now."

## Release

- **Version:** v1.0.0 (Initial public release)
- **Downloads included in this repository:**
    - `release.zip` — contains `bbl-dl.exe` (CLI) and `bilibili_downloader.exe` (GUI) for Windows.
    - `hakiri.ico` — application icon used in the builds.

You can download the packaged executables from the repository Releases page or use the `release.zip` in this repository root. Note: FFmpeg is required at runtime for merging and audio extraction — install it separately and ensure `ffmpeg.exe` is available on PATH.

## Performance Tips

- **Wired connection** is faster than WiFi
- **Close background apps** to maximize bandwidth
- Downloads are cached, so re-downloading the same video is much faster
- Parallel fragment downloads (4 concurrent) significantly speed up large files

## Troubleshooting

### FFmpeg not found error
Install FFmpeg and make sure it's in your system PATH.

### Download fails
- Check your internet connection
- Verify the Bilibili URL is valid
- Make sure you have write permissions in the output folder
- Some videos may have region restrictions

### Slow downloads
- Use a wired connection instead of WiFi
- Check your internet speed
- Try downloading during off-peak hours
- Close other bandwidth-heavy applications


